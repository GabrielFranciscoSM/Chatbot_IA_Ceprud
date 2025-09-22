#!/usr/bin/env python3
"""
Script para extraer información de guías docentes y poblar el RAG Service
Versión migrada al RAG Service - Crea contenido RAG desde guías docentes web
"""
import requests
from bs4 import BeautifulSoup
import re
import json
import argparse
import sys
from urllib.parse import urljoin
from typing import Dict, List, Optional, Any
from pathlib import Path
import tempfile

# Configuración
DEFAULT_RAG_SERVICE_URL = "http://localhost:8082"

class GuiaDocenteScraper:
    """Scraper para extraer información de guías docentes y enviarla al RAG Service"""
    
    def __init__(self, rag_service_url: str = DEFAULT_RAG_SERVICE_URL):
        self.rag_service_url = rag_service_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def check_rag_service(self) -> bool:
        """Verificar que el RAG Service esté disponible"""
        try:
            response = requests.get(f"{self.rag_service_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error conectando al RAG Service: {e}")
            return False
    
    def parse_profesorado(self, profesorado_container) -> List[Dict[str, Any]]:
        """
        Parsea la sección de profesorado y tutorías, ya que su estructura
        de dos columnas es única y no se puede generalizar fácilmente.
        """
        if not profesorado_container:
            return []
        
        profesores_data = {}
        profesores_div = profesorado_container.find('div', class_='profesores')
        
        if profesores_div:
            current_role = None
            for element in profesores_div.find_all(['h3', 'div']):
                if element.name == 'h3':
                    current_role = element.get_text(strip=True)
                elif element.name == 'div' and current_role:
                    text_content = ' '.join(element.get_text(strip=True).split())
                    parts = re.split(r'Grupo(?:s)?:\s*', text_content, maxsplit=1, flags=re.IGNORECASE)
                    nombre_profesor = parts[0].replace('.', '').strip()
                    grupos = parts[1].strip() if len(parts) > 1 and parts[1] is not None else ""
                    
                    if nombre_profesor:
                        if nombre_profesor not in profesores_data:
                            profesores_data[nombre_profesor] = {'nombre': nombre_profesor}
                        profesores_data[nombre_profesor]['rol'] = current_role
                        if grupos:
                            profesores_data[nombre_profesor]['grupos'] = grupos
        
        tutorias_div = profesorado_container.find('div', class_='tutorias')
        if tutorias_div:
            for nombre_h3 in tutorias_div.find_all('h3', class_='nombre'):
                nombre_profesor = nombre_h3.get_text(strip=True)
                if nombre_profesor in profesores_data:
                    tutoria_info_div = nombre_h3.find_next_sibling('div', class_='tutorias')
                    if tutoria_info_div:
                        profesores_data[nombre_profesor]['tutorias'] = tutoria_info_div.get_text(strip=True)
        
        return list(profesores_data.values())
    
    def parse_section_content(self, container, base_url: str) -> Optional[Any]:
        """
        Función generalizada y multicapa:
        1. Intenta parsear como un Temario estructurado.
        2. Si falla, intenta parsear como una lista (conservando enlaces).
        3. Si falla, lo trata como texto plano.
        """
        if not container:
            return None

        def _parse_list_item(li_tag):
            link = li_tag.find('a')
            if link and link.get('href'):
                return {
                    'texto': li_tag.get_text(strip=True),
                    'enlace': urljoin(base_url, link['href'])
                }
            else:
                return li_tag.get_text(strip=True)

        # Verificar si es un temario con estructura específica
        if container.find('div', class_='tema'):
            temas = []
            for tema_div in container.find_all('div', class_='tema'):
                tema_data = {'tema': tema_div.find('h3').get_text(strip=True) if tema_div.find('h3') else "Tema sin título"}
                
                contenidos_div = tema_div.find('div', class_='contenidos')
                if contenidos_div:
                    contenidos_list = contenidos_div.find('ul')
                    if contenidos_list:
                        tema_data['contenidos'] = [_parse_list_item(li) for li in contenidos_list.find_all('li')]
                
                temas.append(tema_data)
            return temas
        
        # Si no es temario, buscar listas generales
        lista = container.find('ul')
        if lista:
            return [_parse_list_item(li) for li in lista.find_all('li')]
        
        # Como fallback, devolver texto plano
        return container.get_text(strip=True)
    
    def scrape_guia_docente(self, url: str) -> Dict[str, Any]:
        """Extraer información completa de una guía docente"""
        try:
            print(f"🔍 Extrayendo guía docente de: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            guia_data = {'url': url}
            
            # Extraer título
            title_tag = soup.find('h1')
            if title_tag:
                guia_data['titulo'] = title_tag.get_text(strip=True)
            
            # Mapeo de secciones
            section_mapping = {
                'datos-generales': 'datos_generales',
                'competencias': 'competencias',
                'objetivos': 'objetivos',
                'contenidos': 'contenidos',
                'planificacion': 'planificacion',
                'metodologias': 'metodologias',
                'personalizacion': 'personalizacion',
                'evaluacion': 'evaluacion',
                'recursos': 'recursos',
                'recomendaciones': 'recomendaciones'
            }
            
            # Extraer cada sección
            for class_name, key in section_mapping.items():
                section = soup.find('div', class_=class_name)
                if section:
                    guia_data[key] = self.parse_section_content(section, url)
            
            # Extraer profesorado (tratamiento especial)
            profesorado_section = soup.find('div', class_='profesorado')
            if profesorado_section:
                guia_data['profesorado'] = self.parse_profesorado(profesorado_section)
            
            print(f"✅ Guía docente extraída: {guia_data.get('titulo', 'Sin título')}")
            return guia_data
            
        except Exception as e:
            print(f"❌ Error extrayendo guía docente de {url}: {e}")
            return {}
    
    def convert_guia_to_text(self, guia_data: Dict[str, Any]) -> str:
        """Convertir datos de guía docente a texto estructurado para RAG"""
        if not guia_data:
            return ""
        
        text_parts = []
        
        # Título
        if 'titulo' in guia_data:
            text_parts.append(f"# {guia_data['titulo']}\n")
        
        # Datos generales
        if 'datos_generales' in guia_data and guia_data['datos_generales']:
            text_parts.append("## Datos Generales")
            if isinstance(guia_data['datos_generales'], str):
                text_parts.append(guia_data['datos_generales'])
            text_parts.append("")
        
        # Competencias
        if 'competencias' in guia_data and guia_data['competencias']:
            text_parts.append("## Competencias")
            self._format_content(text_parts, guia_data['competencias'])
            text_parts.append("")
        
        # Objetivos
        if 'objetivos' in guia_data and guia_data['objetivos']:
            text_parts.append("## Objetivos")
            self._format_content(text_parts, guia_data['objetivos'])
            text_parts.append("")
        
        # Contenidos/Temario
        if 'contenidos' in guia_data and guia_data['contenidos']:
            text_parts.append("## Contenidos y Temario")
            self._format_content(text_parts, guia_data['contenidos'])
            text_parts.append("")
        
        # Metodologías
        if 'metodologias' in guia_data and guia_data['metodologias']:
            text_parts.append("## Metodologías Docentes")
            self._format_content(text_parts, guia_data['metodologias'])
            text_parts.append("")
        
        # Evaluación
        if 'evaluacion' in guia_data and guia_data['evaluacion']:
            text_parts.append("## Evaluación")
            self._format_content(text_parts, guia_data['evaluacion'])
            text_parts.append("")
        
        # Recursos
        if 'recursos' in guia_data and guia_data['recursos']:
            text_parts.append("## Recursos")
            self._format_content(text_parts, guia_data['recursos'])
            text_parts.append("")
        
        # Profesorado
        if 'profesorado' in guia_data and guia_data['profesorado']:
            text_parts.append("## Profesorado")
            for profesor in guia_data['profesorado']:
                if isinstance(profesor, dict):
                    text_parts.append(f"**{profesor.get('nombre', 'Sin nombre')}**")
                    if 'rol' in profesor:
                        text_parts.append(f"- Rol: {profesor['rol']}")
                    if 'grupos' in profesor:
                        text_parts.append(f"- Grupos: {profesor['grupos']}")
                    if 'tutorias' in profesor:
                        text_parts.append(f"- Tutorías: {profesor['tutorias']}")
                    text_parts.append("")
        
        return "\n".join(text_parts)
    
    def _format_content(self, text_parts: List[str], content: Any) -> None:
        """Formatear contenido según su tipo"""
        if isinstance(content, str):
            text_parts.append(content)
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    if 'tema' in item:  # Es un tema del temario
                        text_parts.append(f"### {item['tema']}")
                        if 'contenidos' in item:
                            for contenido in item['contenidos']:
                                if isinstance(contenido, dict) and 'texto' in contenido:
                                    text_parts.append(f"- {contenido['texto']}")
                                else:
                                    text_parts.append(f"- {contenido}")
                    elif 'texto' in item:  # Es un item con enlace
                        text_parts.append(f"- {item['texto']}")
                    else:
                        text_parts.append(f"- {item}")
                else:
                    text_parts.append(f"- {item}")
        else:
            text_parts.append(str(content))
    
    def populate_rag_from_guia(self, url: str, subject_name: str, reset: bool = False) -> bool:
        """Extraer guía docente y poblar RAG Service"""
        try:
            # Extraer datos de la guía
            guia_data = self.scrape_guia_docente(url)
            if not guia_data:
                print(f"❌ No se pudo extraer información de {url}")
                return False
            
            # Convertir a texto
            text_content = self.convert_guia_to_text(guia_data)
            if not text_content:
                print(f"❌ No se pudo generar contenido de texto para {subject_name}")
                return False
            
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(text_content)
                temp_file_path = temp_file.name
            
            try:
                # Enviar al RAG Service
                with open(temp_file_path, 'rb') as f:
                    files = {'files': (f'guia_docente_{subject_name}.txt', f, 'text/plain')}
                    data = {
                        'subject': subject_name,
                        'reset': str(reset).lower()
                    }
                    
                    print(f"🔄 Enviando guía docente al RAG Service...")
                    response = requests.post(
                        f"{self.rag_service_url}/populate",
                        files=files,
                        data=data,
                        timeout=120
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    chunks_added = result.get('chunks_added', 0)
                    print(f"✅ Guía docente de {subject_name} poblada exitosamente ({chunks_added} chunks)")
                    
                    # Guardar JSON local también
                    json_path = Path(f"guia_docente_{subject_name}.json")
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(guia_data, f, indent=2, ensure_ascii=False)
                    print(f"💾 Datos guardados en: {json_path}")
                    
                    return True
                else:
                    print(f"❌ Error poblando RAG Service: HTTP {response.status_code}")
                    print(f"   Detalle: {response.text}")
                    return False
            
            finally:
                # Limpiar archivo temporal
                try:
                    Path(temp_file_path).unlink()
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ Error procesando guía docente: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Extraer guías docentes y poblar RAG Service",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Extraer y poblar una guía docente
  python guia_docente_scrapper.py --url "https://..." --subject "metaheuristicas"
  
  # Resetear base de datos antes de poblar
  python guia_docente_scrapper.py --url "https://..." --subject "estadistica" --reset
  
  # Usar RAG Service remoto
  python guia_docente_scrapper.py --url "https://..." --subject "algoritmos" --rag-url "http://remote:8082"
        """
    )
    
    parser.add_argument(
        "--url", 
        required=True,
        help="URL de la guía docente a extraer"
    )
    parser.add_argument(
        "--subject", 
        required=True,
        help="Nombre de la asignatura para el RAG Service"
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
    
    args = parser.parse_args()
    
    print("🌐 Guía Docente Scraper para RAG Service")
    print(f"🔗 URL: {args.url}")
    print(f"📚 Asignatura: {args.subject}")
    print(f"🔄 Reset: {'Sí' if args.reset else 'No'}")
    print(f"🌐 RAG Service: {args.rag_url}")
    print("=" * 70)
    
    # Crear scraper
    scraper = GuiaDocenteScraper(args.rag_url)
    
    # Verificar RAG Service
    if not scraper.check_rag_service():
        print("❌ RAG Service no está disponible")
        sys.exit(1)
    print("✅ RAG Service disponible")
    
    # Extraer y poblar
    success = scraper.populate_rag_from_guia(
        url=args.url,
        subject_name=args.subject,
        reset=args.reset
    )
    
    if success:
        print("\n🎉 Proceso completado exitosamente")
    else:
        print("\n❌ Proceso falló")
        sys.exit(1)


if __name__ == "__main__":
    main()
