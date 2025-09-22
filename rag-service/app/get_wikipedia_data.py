#!/usr/bin/env python3
"""
Script para extraer contenido de Wikipedia y poblar el RAG Service
Versión migrada al RAG Service - Obtiene artículos de Wikipedia como contenido RAG
"""
import wikipedia
import re
import argparse
import sys
import requests
import tempfile
from pathlib import Path
from typing import List, Optional, Set
import time

# Configuración
DEFAULT_RAG_SERVICE_URL = "http://localhost:8082"

class WikipediaRAGPopulator:
    """Clase para extraer contenido de Wikipedia y enviarlo al RAG Service"""
    
    def __init__(self, rag_service_url: str = DEFAULT_RAG_SERVICE_URL, language: str = 'es'):
        self.rag_service_url = rag_service_url
        self.language = language
        wikipedia.set_lang(language)
        
    def check_rag_service(self) -> bool:
        """Verificar que el RAG Service esté disponible"""
        try:
            response = requests.get(f"{self.rag_service_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error conectando al RAG Service: {e}")
            return False
    
    def clean_wikipedia_text(self, content: str) -> str:
        """
        Limpia específicamente texto de artículos de Wikipedia para RAG.
        Elimina marcado específico de Wikipedia y mejora la legibilidad.
        """
        
        # 1. Eliminar secciones de referencias y enlaces externos
        content = re.sub(r"== Referencias ==.*?(?=== |$)", "", content, flags=re.DOTALL)
        content = re.sub(r"== Enlaces externos ==.*?(?=== |$)", "", content, flags=re.DOTALL)
        content = re.sub(r"== Véase también ==.*?(?=== |$)", "", content, flags=re.DOTALL)
        content = re.sub(r"== Bibliografía ==.*?(?=== |$)", "", content, flags=re.DOTALL)
        content = re.sub(r"== Pseudocódigo ==.*?(?=== |$)", "", content, flags=re.DOTALL)
        content = re.sub(r"== Algoritmo ==.*?(?=== |$)", "", content, flags=re.DOTALL)
        content = re.sub(r"== Esquema ==.*?(?=== |$)", "", content, flags=re.DOTALL)

        # 2. Eliminar texto entre llaves {} - plantillas, fórmulas, etc.
        content = re.sub(r"\{[^}]*\}", "", content)
        
        # 3. Limpiar expresiones matemáticas LaTeX/MathML
        # Eliminar bloques de fórmulas matemáticas que aparecen como texto plano
        content = re.sub(r"\s*\{\s*\\displaystyle[^}]*\}\s*", " ", content)
        content = re.sub(r"\s*\{\s*\\[a-zA-Z]+[^}]*\}\s*", " ", content)
            
        # 4. Limpiar encabezados de sección (convertir === === a formato más limpio)
        content = re.sub(r"^=+\s*(.+?)\s*=+$", r"\1:", content, flags=re.MULTILINE)
        
        # 5. Eliminar líneas que contengan solo espacios y caracteres especiales
        content = re.sub(r"^\s*[⊆∪∖∅≠←→∈]+\s*$", "", content, flags=re.MULTILINE)
        
        # 6. Eliminar referencias a figuras, imágenes y tablas
        content = re.sub(r"\[\[Archivo:.*?\]\]", "", content)
        content = re.sub(r"\[\[Imagen:.*?\]\]", "", content)
        content = re.sub(r"\[\[File:.*?\]\]", "", content)
        
        # 7. Limpiar enlaces internos de Wikipedia [[enlace|texto]] -> texto
        content = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r"\2", content)  # [[enlace|texto]] -> texto
        content = re.sub(r"\[\[([^\]]+)\]\]", r"\1", content)  # [[enlace]] -> enlace
        
        # 8. Eliminar plantillas y parámetros {{plantilla}} (redundante con paso 2, pero se mantiene por seguridad)
        content = re.sub(r"\{\{[^}]*\}\}", "", content)
            
        # Eliminar bloques de código que contengan palabras clave de programación
        content = re.sub(r"procedure\s+\w+.*?end procedure\.?", "", content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r"algorithm\s+\w+.*?end algorithm\.?", "", content, flags=re.DOTALL | re.IGNORECASE)
        
        # Eliminar líneas típicas de pseudocódigo
        content = re.sub(r"^\s*(while|if|begin|end).*$", "", content, flags=re.MULTILINE | re.IGNORECASE)
        
        # 9. Normalizar espacios múltiples y líneas vacías
        content = re.sub(r"[ \t]+", " ", content)  # Espacios múltiples -> un espacio
        content = re.sub(r"\n{3,}", "\n\n", content)  # Máximo dos saltos de línea
        
        # 10. Eliminar líneas que sean solo números o caracteres especiales
        content = re.sub(r"^\s*\d+\s*$", "", content, flags=re.MULTILINE)
        content = re.sub(r"^\s*[^\w\s]+\s*$", "", content, flags=re.MULTILINE)
        
        return content.strip()
    
    def search_wikipedia_articles(self, query: str, max_results: int = 10) -> List[str]:
        """Buscar artículos de Wikipedia relacionados con una consulta"""
        try:
            print(f"🔍 Buscando artículos de Wikipedia para: '{query}'")
            search_results = wikipedia.search(query, results=max_results)
            print(f"📄 Encontrados {len(search_results)} artículos potenciales")
            return search_results
        except Exception as e:
            print(f"❌ Error buscando en Wikipedia: {e}")
            return []
    
    def get_wikipedia_article(self, title: str) -> Optional[str]:
        """Obtener contenido completo de un artículo de Wikipedia"""
        try:
            print(f"📖 Obteniendo artículo: {title}")
            
            # Obtener página con retry en caso de ambigüedad
            try:
                page = wikipedia.page(title, auto_suggest=True)
            except wikipedia.DisambiguationError as e:
                # Si hay ambigüedad, tomar la primera opción
                print(f"⚠️  Ambigüedad detectada para '{title}', usando: {e.options[0]}")
                page = wikipedia.page(e.options[0])
            except wikipedia.PageError:
                print(f"❌ Página no encontrada: {title}")
                return None
            
            # Obtener contenido y limpiar
            content = page.content
            cleaned_content = self.clean_wikipedia_text(content)
            
            if len(cleaned_content) < 200:  # Artículo muy corto
                print(f"⚠️  Artículo muy corto, omitiendo: {title}")
                return None
            
            # Añadir metadatos al inicio
            article_text = f"# {page.title}\n\n"
            article_text += f"**URL:** {page.url}\n\n"
            article_text += cleaned_content
            
            print(f"✅ Artículo obtenido: {title} ({len(cleaned_content)} caracteres)")
            return article_text
            
        except Exception as e:
            print(f"❌ Error obteniendo artículo '{title}': {e}")
            return None
    
    def get_multiple_articles(self, terms: List[str], max_per_term: int = 3) -> List[str]:
        """Obtener múltiples artículos de Wikipedia"""
        all_articles = []
        processed_titles = set()  # Para evitar duplicados
        
        for term in terms:
            print(f"\n🔍 Procesando término: {term}")
            
            # Buscar artículos relacionados
            search_results = self.search_wikipedia_articles(term, max_results=max_per_term * 2)
            
            articles_for_term = 0
            for title in search_results:
                if articles_for_term >= max_per_term:
                    break
                
                if title.lower() in processed_titles:
                    print(f"⏭️  Omitiendo duplicado: {title}")
                    continue
                
                article_content = self.get_wikipedia_article(title)
                if article_content:
                    all_articles.append(article_content)
                    processed_titles.add(title.lower())
                    articles_for_term += 1
                
                # Pausa para evitar rate limiting
                time.sleep(0.5)
        
        print(f"\n📚 Total de artículos obtenidos: {len(all_articles)}")
        return all_articles
    
    def populate_rag_from_wikipedia(self, terms: List[str], subject_name: str, 
                                   max_per_term: int = 3, reset: bool = False) -> bool:
        """Obtener artículos de Wikipedia y poblar RAG Service"""
        try:
            # Obtener artículos
            articles = self.get_multiple_articles(terms, max_per_term)
            
            if not articles:
                print("❌ No se pudieron obtener artículos de Wikipedia")
                return False
            
            # Crear archivos temporales para cada artículo
            temp_files = []
            try:
                for i, article in enumerate(articles):
                    temp_file = tempfile.NamedTemporaryFile(
                        mode='w', 
                        suffix=f'_wikipedia_article_{i+1}.txt',
                        delete=False, 
                        encoding='utf-8'
                    )
                    temp_file.write(article)
                    temp_file.close()
                    temp_files.append(temp_file.name)
                
                # Preparar archivos para envío
                files = []
                for temp_path in temp_files:
                    with open(temp_path, 'rb') as f:
                        filename = f"wikipedia_{Path(temp_path).stem}.txt"
                        files.append(('files', (filename, f.read(), 'text/plain')))
                
                # Enviar al RAG Service
                data = {
                    'subject': subject_name,
                    'reset': str(reset).lower()
                }
                
                print(f"\n🔄 Enviando {len(files)} artículos al RAG Service...")
                response = requests.post(
                    f"{self.rag_service_url}/populate",
                    files=files,
                    data=data,
                    timeout=300  # 5 minutos
                )
                
                if response.status_code == 200:
                    result = response.json()
                    chunks_added = result.get('chunks_added', 0)
                    processed_files = result.get('processed_files', [])
                    failed_files = result.get('failed_files', [])
                    
                    print(f"✅ Wikipedia para {subject_name} poblada exitosamente")
                    print(f"📊 Chunks añadidos: {chunks_added}")
                    print(f"📊 Archivos procesados: {len(processed_files)}")
                    
                    if failed_files:
                        print(f"⚠️  Archivos fallidos: {len(failed_files)}")
                    
                    return True
                else:
                    print(f"❌ Error poblando RAG Service: HTTP {response.status_code}")
                    print(f"   Detalle: {response.text}")
                    return False
            
            finally:
                # Limpiar archivos temporales
                for temp_path in temp_files:
                    try:
                        Path(temp_path).unlink()
                    except:
                        pass
                        
        except Exception as e:
            print(f"❌ Error procesando Wikipedia: {e}")
            return False
    
    def save_articles_locally(self, terms: List[str], output_dir: str = "wikipedia_articles", 
                             max_per_term: int = 3) -> bool:
        """Guardar artículos de Wikipedia localmente"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            articles = self.get_multiple_articles(terms, max_per_term)
            
            for i, article in enumerate(articles):
                # Extraer título del artículo
                title_match = re.match(r"# (.+)", article)
                title = title_match.group(1) if title_match else f"articulo_{i+1}"
                
                # Crear nombre de archivo seguro
                safe_filename = re.sub(r'[^\w\s-]', '', title)
                safe_filename = re.sub(r'[-\s]+', '_', safe_filename)
                
                file_path = output_path / f"{safe_filename}.txt"
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(article)
                
                print(f"💾 Guardado: {file_path}")
            
            print(f"\n🎉 {len(articles)} artículos guardados en {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error guardando artículos: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Extraer artículos de Wikipedia y poblar RAG Service",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Poblar con términos específicos
  python get_wikipedia_data.py --terms "algoritmo genético" "metaheurística" "optimización" --subject "metaheuristicas"
  
  # Más artículos por término
  python get_wikipedia_data.py --terms "estadística" "probabilidad" --subject "estadistica" --max-per-term 5
  
  # Resetear antes de poblar
  python get_wikipedia_data.py --terms "servidor web" "nginx" --subject "servidores" --reset
  
  # Solo guardar localmente sin poblar RAG
  python get_wikipedia_data.py --terms "algoritmo" --save-only --output-dir "articulos_algoritmos"
  
  # Usar Wikipedia en inglés
  python get_wikipedia_data.py --terms "genetic algorithm" --subject "algorithms" --language "en"
        """
    )
    
    parser.add_argument(
        "--terms", 
        nargs="+",
        required=True,
        help="Términos de búsqueda para Wikipedia"
    )
    parser.add_argument(
        "--subject", 
        help="Nombre de la asignatura para el RAG Service (requerido si no se usa --save-only)"
    )
    parser.add_argument(
        "--max-per-term", 
        type=int,
        default=3,
        help="Máximo número de artículos por término (por defecto: 3)"
    )
    parser.add_argument(
        "--rag-url", 
        default=DEFAULT_RAG_SERVICE_URL,
        help=f"URL del RAG Service (por defecto: {DEFAULT_RAG_SERVICE_URL})"
    )
    parser.add_argument(
        "--reset", 
        action="store_true",
        help="Resetear base de datos de la asignatura antes de poblar"
    )
    parser.add_argument(
        "--language", 
        default="es",
        help="Idioma de Wikipedia (por defecto: es)"
    )
    parser.add_argument(
        "--save-only", 
        action="store_true",
        help="Solo guardar artículos localmente sin poblar RAG Service"
    )
    parser.add_argument(
        "--output-dir", 
        default="wikipedia_articles",
        help="Directorio para guardar artículos localmente (por defecto: wikipedia_articles)"
    )
    
    args = parser.parse_args()
    
    # Validar argumentos
    if not args.save_only and not args.subject:
        print("❌ --subject es requerido cuando no se usa --save-only")
        sys.exit(1)
    
    print("📚 Wikipedia RAG Populator")
    print(f"🔍 Términos: {args.terms}")
    print(f"📊 Max por término: {args.max_per_term}")
    print(f"🌐 Idioma: {args.language}")
    
    if args.save_only:
        print(f"💾 Modo: Solo guardar en {args.output_dir}")
    else:
        print(f"📚 Asignatura: {args.subject}")
        print(f"🔄 Reset: {'Sí' if args.reset else 'No'}")
        print(f"🌐 RAG Service: {args.rag_url}")
    
    print("=" * 70)
    
    # Crear populator
    populator = WikipediaRAGPopulator(args.rag_url, args.language)
    
    if args.save_only:
        # Solo guardar localmente
        success = populator.save_articles_locally(
            terms=args.terms,
            output_dir=args.output_dir,
            max_per_term=args.max_per_term
        )
    else:
        # Verificar RAG Service
        if not populator.check_rag_service():
            print("❌ RAG Service no está disponible")
            sys.exit(1)
        print("✅ RAG Service disponible")
        
        # Poblar RAG Service
        success = populator.populate_rag_from_wikipedia(
            terms=args.terms,
            subject_name=args.subject,
            max_per_term=args.max_per_term,
            reset=args.reset
        )
    
    if success:
        print("\n🎉 Proceso completado exitosamente")
    else:
        print("\n❌ Proceso falló")
        sys.exit(1)


if __name__ == "__main__":
    main()
