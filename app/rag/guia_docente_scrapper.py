import requests
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urljoin

def parse_profesorado(profesorado_container):
    """
    Parsea la sección de profesorado y tutorías, ya que su estructura
    de dos columnas es única y no se puede generalizar fácilmente.
    """
    if not profesorado_container: return []
    profesores_data = {}
    profesores_div = profesorado_container.find('div', class_='profesores')
    if profesores_div:
        current_role = None
        for element in profesores_div.find_all(['h3', 'div']):
            if element.name == 'h3': current_role = element.get_text(strip=True)
            elif element.name == 'div' and current_role:
                text_content = ' '.join(element.get_text(strip=True).split())
                parts = re.split(r'Grupo(?:s)?:\s*', text_content, maxsplit=1, flags=re.IGNORECASE)
                nombre_profesor = parts[0].replace('.', '').strip()
                grupos = parts[1].strip() if len(parts) > 1 and parts[1] is not None else ""
                if nombre_profesor:
                    if nombre_profesor not in profesores_data:
                        profesores_data[nombre_profesor] = {'nombre': nombre_profesor}
                    profesores_data[nombre_profesor]['rol'] = current_role
                    if grupos: profesores_data[nombre_profesor]['grupos'] = grupos
    tutorias_div = profesorado_container.find('div', class_='tutorias')
    if tutorias_div:
        for nombre_h3 in tutorias_div.find_all('h3', class_='nombre'):
            nombre_profesor = nombre_h3.get_text(strip=True)
            if nombre_profesor in profesores_data:
                tutoria_info_div = nombre_h3.find_next_sibling('div', class_='tutorias')
                if tutoria_info_div:
                    profesores_data[nombre_profesor]['tutorias'] = tutoria_info_div.get_text(strip=True)
    return list(profesores_data.values())

def parse_section_content(container, base_url):
    """
    Función generalizada y multicapa:
    1. Intenta parsear como un Temario estructurado.
    2. Si falla, intenta parsear como una lista (conservando enlaces).
    3. Si falla, lo trata como texto plano.
    """
    if not container: return None

    def _parse_list_item(li_tag):
        link = li_tag.find('a')
        if link and link.get('href'):
            url = urljoin(base_url, link.get('href'))
            return {'text': li_tag.get_text(strip=True), 'url': url}
        return li_tag.get_text(strip=True)

    subtitulos = container.find_all('h3')
    if subtitulos:
        categorized_data = {}
        for h3 in subtitulos:
            category_key = h3.get_text(strip=True).lower().replace(' ', '_')
            content_block = h3.find_next_sibling(['div', 'ul'])
            if content_block:
                content_text = content_block.get_text(strip=True, separator='\n')
                topic_starters_regex = r'^(Tema\s+\d+:.*|Prácticas\s+en.*:|Seminarios\s*)$'
                
                if re.search(topic_starters_regex, content_text, re.MULTILINE):
                    temario = []
                    lines = content_text.split('\n')
                    current_topic = None
                    for line in lines:
                        if re.match(topic_starters_regex, line.strip()):
                            if current_topic: temario.append(current_topic)
                            current_topic = {'tema': line.strip(), 'puntos': []}
                        elif current_topic:
                            current_topic['puntos'].append(line.strip())
                    if current_topic: temario.append(current_topic)
                    categorized_data[category_key] = temario
                else:
                    list_items = content_block.find_all('li')
                    if list_items:
                        categorized_data[category_key] = [_parse_list_item(li) for li in list_items]
                    else:
                        categorized_data[category_key] = content_text
        return categorized_data

    list_items = container.find_all('li')
    if list_items:
        return [_parse_list_item(li) for li in list_items]

    return container.get_text(strip=True, separator='\n')

def scrape_guia_docente_ugr(url):
    """Extrae información detallada de una guía docente de la UGR."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al acceder a la URL: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    info = {}
    info['asignatura'] = soup.find('h1', class_='page-title').get_text(strip=True) if soup.find('h1', class_='page-title') else soup.title.string.split('|')[0].strip()
    
    guia_container = soup.find('div', class_='guia-docente')
    if not guia_container: return info

    profesorado_container = guia_container.find('div', class_='profesorado row')
    if profesorado_container:
        info['profesorado_y_tutorias'] = parse_profesorado(profesorado_container)

    secciones_a_ignorar = ['Profesorado', 'Tutorías']
    for h2_title in guia_container.find_all('h2', class_='active-base'):
        key_raw = h2_title.get_text(strip=True)
        if key_raw in secciones_a_ignorar: continue

        key = re.sub(r' \([^)]*\)', '', key_raw).lower().replace(' ', '_').replace('y/o', 'o')
        
        parent_row = h2_title.find_parent(class_='row')
        content_container = parent_row if parent_row else h2_title.find_next_sibling('div')

        if content_container:
            info[key] = parse_section_content(content_container, url)

    return info

def guardar_en_json(datos, nombre_archivo):
    """Guarda el diccionario de datos en un archivo JSON."""
    try:
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
        print(f"✅ ¡Datos guardados correctamente en el archivo '{nombre_archivo}'!")
    except IOError as e:
        print(f"Error al escribir en el archivo: {e}")

if __name__ == '__main__':
    #url_guia = 'https://grados.ugr.es/ramas/ingenieria-arquitectura/grado-ingenieria-informatica/metaheuristicas-especialidad-computacion-y-sistemas-inteligentes/guia-docente'
    url_guia = "https://www.ugr.es/estudiantes/grados/grado-ingenieria-informatica/modelos-avanzados-computacionecompsist/guia-docente"
    print(f"Extrayendo datos de: {url_guia}")
    datos_guia = scrape_guia_docente_ugr(url_guia)
    if datos_guia:
        print("Datos extraídos con éxito.")
        titulo_asignatura = datos_guia.get('asignatura', 'guia_docente_sin_titulo')
        nombre_base = re.sub(r'[^\w\s-]', '', titulo_asignatura).strip().lower()
        nombre_archivo = re.sub(r'[-\s]+', '_', nombre_base) + '.json'
        guardar_en_json(datos_guia, nombre_archivo)