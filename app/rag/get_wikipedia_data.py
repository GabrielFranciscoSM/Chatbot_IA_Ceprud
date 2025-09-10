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

# Ejemplo de uso y test
if __name__ == "__main__":
    # Test con el texto actual
    wikipedia.set_lang("es")
    
    print("=== BÚSQUEDA Y DESCARGA ===")
    query = "Concepto y elementos de los algoritmos basados en poblaciones"
    article = get_wikipedia_article(query)
    
    if article:
        print(f"Título: {article['title']}")
        print(f"URL: {article['url']}")
        print("\n=== CONTENIDO LIMPIO ===")
        print(article['content'][:1000] + "..." if len(article['content']) > 1000 else article['content'])
        
        # Guardar el artículo limpio
        with open("wikitext_cleaned.txt", "w", encoding="utf-8") as f:
            f.write(article['content'])
        print("\n✅ Texto limpio guardado en wikitext_cleaned.txt")
    
    # # Ejemplo de descarga múltiple
    # print("\n=== DESCARGA MÚLTIPLE ===")
    # topics = [
    #     "algoritmo voraz",
    #     "programación dinámica", 
    #     "algoritmo de Dijkstra",
    #     "inteligencia artificial"
    # ]
    
    # save_wikipedia_articles(topics, "data/wikipedia_articles")
    # print("✅ Artículos guardados en data/wikipedia_articles")
