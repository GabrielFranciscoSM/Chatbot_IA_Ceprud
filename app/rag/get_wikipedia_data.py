from wikipedia import wikipedia
import re

def clean_wikipedia_text(content: str) -> str:
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
    content = re.sub(r"^\s*(for each|while|if|then|else|endif|endfor|endwhile|do|begin|end).*$", "", content, flags=re.MULTILINE | re.IGNORECASE)
    
    # Eliminar líneas con operadores de asignación y comparación típicos de pseudocódigo
    content = re.sub(r"^\s*\w+\s*(:=|=|←|→|\+=|-=)\s*.*$", "", content, flags=re.MULTILINE)
    
    # 10. Eliminar líneas con pocos caracteres (menos de 10 caracteres útiles)
    # Esto elimina líneas que solo contienen espacios, números sueltos, o texto muy corto
    lines = content.split('\n')
    filtered_lines = []
    for line in lines:
        # Conservar líneas vacías para mantener la estructura de párrafos
        if line.strip() == "":
            filtered_lines.append(line)
        # Conservar líneas con al menos 10 caracteres útiles (sin espacios)
        elif len(re.sub(r'[^\w\s]', '', line.strip())) >= 10:
            filtered_lines.append(line)
        # Conservar encabezados cortos que terminan en ":"
        elif line.strip().endswith(':') and len(line.strip()) > 3:
            filtered_lines.append(line)
    content = '\n'.join(filtered_lines)
            
    # 11. Normalizar espacios múltiples
    content = re.sub(r" {2,}", " ", content)
    
    # 12. Eliminar líneas vacías múltiples
    content = re.sub(r"\n\s*\n\s*\n", "\n\n", content)
    
    
    return content.strip()

def get_wikipedia_article(query: str, lang: str = "es") -> dict:
    """
    Obtiene un artículo de Wikipedia y lo limpia para RAG.
    
    Args:
        query: Término de búsqueda
        lang: Idioma de Wikipedia (por defecto español)
    
    Returns:
        Dict con título, contenido limpio, resumen y metadatos
    """
    try:
        wikipedia.set_lang(lang)
        
        # Buscar el artículo
        search_results = wikipedia.search(query, results=5)
        if not search_results:
            return None
        
        # Intentar obtener la página con el primer resultado
        page = wikipedia.page(search_results[0])
        
        # Limpiar el contenido
        cleaned_content = clean_wikipedia_text(page.content)
        
        return {
            "title": page.title,
            "url": page.url,
            "summary": page.summary,
            "content": cleaned_content,
            "categories": getattr(page, 'categories', []),
            "lang": lang,
            "search_query": query
        }
        
    except wikipedia.DisambiguationError as e:
        # Si hay desambiguación, tomar la primera opción
        try:
            page = wikipedia.page(e.options[0])
            cleaned_content = clean_wikipedia_text(page.content)
            return {
                "title": page.title,
                "url": page.url,
                "summary": page.summary,
                "content": cleaned_content,
                "categories": getattr(page, 'categories', []),
                "lang": lang,
                "search_query": query
            }
        except Exception as inner_e:
            print(f"Error al procesar página desambiguada: {inner_e}")
            return None
            
    except wikipedia.PageError:
        print(f"No se encontró la página para: {query}")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None

def save_wikipedia_articles(queries: list, output_dir: str = "data/wikipedia", lang: str = "es"):
    """
    Descarga y guarda múltiples artículos de Wikipedia limpiados.
    
    Args:
        queries: Lista de términos de búsqueda
        output_dir: Directorio donde guardar los archivos
        lang: Idioma de Wikipedia
    """
    import os
    import json
    
    # Crear directorio si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    for query in queries:
        print(f"Procesando: {query}")
        article_data = get_wikipedia_article(query, lang)
        
        if article_data:
            # Crear nombre de archivo seguro
            safe_filename = re.sub(r'[^\w\s-]', '', article_data['title']).strip()
            safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
            
            # Guardar contenido limpio como texto
            text_file = os.path.join(output_dir, f"{safe_filename}.txt")
            with open(text_file, "w", encoding="utf-8") as f:
                f.write(f"{article_data['content']}")
                        
            print(f"✅ Guardado: {safe_filename}")
        else:
            print(f"❌ No se pudo procesar: {query}")

def process_terminos_clave(
    terminos_file: str = "./terminos_clave.md", 
    base_output_dir: str = "data",
    lang: str = "es"
):
    """
    Lee el archivo terminos_clave.md y descarga artículos de Wikipedia
    organizados por secciones.
    
    Args:
        terminos_file: Ruta al archivo terminos_clave.md
        base_output_dir: Directorio base donde crear las carpetas por sección
        lang: Idioma de Wikipedia
    """
    import os
    
    try:
        with open(terminos_file, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo: {terminos_file}")
        return
    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")
        return
    
    # Parsear el contenido por secciones
    sections = {}
    current_section = None
    
    for line in content.split('\n'):
        line = line.strip()
        
        # Detectar nueva sección (líneas que empiezan con #)
        if line.startswith('# '):
            current_section = line[2:].strip()  # Quitar '# '
            sections[current_section] = []
            print(f"📁 Sección encontrada: {current_section}")
            
        # Agregar términos a la sección actual (líneas no vacías que no empiecen con #)
        elif line and not line.startswith('#') and current_section:
            sections[current_section].append(line)
    
    print(f"\n📋 Total de secciones encontradas: {len(sections)}")
    
    # Procesar cada sección
    for section_name, terms in sections.items():
        if not terms:  # Saltar secciones vacías
            continue
            
        print(f"\n🔄 Procesando sección: {section_name}")
        print(f"📝 Términos a procesar: {len(terms)}")
        
        # Crear directorio para la sección
        section_dir = os.path.join(base_output_dir, section_name)
        os.makedirs(section_dir, exist_ok=True)
        
        # Procesar cada término en la sección
        successful_downloads = 0
        failed_downloads = 0
        
        for i, term in enumerate(terms, 1):
            print(f"  [{i}/{len(terms)}] Descargando: {term}")
            
            article_data = get_wikipedia_article(term, lang)
            
            if article_data:
                # Crear nombre de archivo seguro
                safe_filename = re.sub(r'[^\w\s-]', '', term).strip()
                safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
                
                # Guardar contenido limpio como texto
                text_file = os.path.join(section_dir, f"{safe_filename}.txt")
                
                try:
                    with open(text_file, "w", encoding="utf-8") as f:
                        # Incluir metadatos al inicio del archivo
                        f.write(article_data['content'])
                    
                    print(f"    ✅ Guardado: {safe_filename}.txt")
                    successful_downloads += 1
                    
                except Exception as e:
                    print(f"    ❌ Error al guardar {safe_filename}: {e}")
                    failed_downloads += 1
            else:
                print(f"    ❌ No se pudo obtener: {term}")
                failed_downloads += 1
        
        print(f"  📊 Sección {section_name}: {successful_downloads} exitosos, {failed_downloads} fallidos")
    
    print(f"\n🎉 Proceso completado. Revisa el directorio '{base_output_dir}' para ver los resultados.")

# Ejemplo de uso y test
if __name__ == "__main__":
    import sys
    
    # Configurar idioma de Wikipedia
    wikipedia.set_lang("es")
    
    print("=== PROCESADOR DE TÉRMINOS CLAVE DE WIKIPEDIA ===")
    print("Este script procesará el archivo terminos_clave.md y descargará")
    print("artículos de Wikipedia organizados por secciones.\n")
    
    # Permitir argumentos de línea de comandos para personalizar
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("Uso:")
            print("  python get_wikipedia_data.py                    # Usar configuración por defecto")
            print("  python get_wikipedia_data.py --custom          # Configuración personalizada")
            print("  python get_wikipedia_data.py --test TÉRMINO    # Probar con un término específico")
            print("  python get_wikipedia_data.py --help            # Mostrar esta ayuda")
            sys.exit(0)
        
        elif sys.argv[1] == "--test" and len(sys.argv) > 2:
            # Modo test con un término específico
            test_term = " ".join(sys.argv[2:])
            print(f"=== MODO TEST: {test_term} ===")
            article = get_wikipedia_article(test_term)
            
            if article:
                print(f"✅ Título: {article['title']}")
                print(f"🔗 URL: {article['url']}")
                print(f"📝 Resumen: {article['summary'][:200]}...")
                print(f"📄 Contenido: {len(article['content'])} caracteres")
                
                # Guardar el artículo de prueba
                with open(f"test_{test_term.replace(' ', '_')}.txt", "w", encoding="utf-8") as f:
                    f.write(article['content'])
                print(f"💾 Guardado en: test_{test_term.replace(' ', '_')}.txt")
            else:
                print(f"❌ No se pudo obtener el artículo para: {test_term}")
            sys.exit(0)
        
        elif sys.argv[1] == "--custom":
            # Modo personalizado
            print("=== CONFIGURACIÓN PERSONALIZADA ===")
            terminos_file = input("Archivo de términos [app/rag/terminos_clave.md]: ").strip()
            if not terminos_file:
                terminos_file = "app/rag/terminos_clave.md"
            
            output_dir = input("Directorio de salida [data]: ").strip()
            if not output_dir:
                output_dir = "data"
            
            lang = input("Idioma Wikipedia [es]: ").strip()
            if not lang:
                lang = "es"
            
            wikipedia.set_lang(lang)
            process_terminos_clave(terminos_file, output_dir, lang)
            sys.exit(0)
    
    # Modo por defecto: procesar términos clave
    print("Iniciando procesamiento con configuración por defecto...")
    print("📁 Archivo: ./terminos_clave.md")
    print("📂 Directorio de salida: data/")
    print("🌐 Idioma: español")
    print("=" * 60)
    
    try:
        process_terminos_clave()
        print("\n🎉 ¡Procesamiento completado exitosamente!")
        print("💡 Consejo: Usa --help para ver más opciones")
    except KeyboardInterrupt:
        print("\n⚠️  Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante el procesamiento: {e}")
        print("💡 Prueba con --test TÉRMINO para verificar la conectividad")
