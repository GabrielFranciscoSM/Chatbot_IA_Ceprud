try:
    from rag.get_wikipedia_data import save_wikipedia_articles
except ImportError:
    from get_wikipedia_data import save_wikipedia_articles

import os
import json
import re

secciones_importantes = [
    "breve_descripción_de_contenidos",
    "resultados_de_aprendizaje",
    "programa_de_contenidos_teóricos_y_prácticos"
]

separadores = [",",".",":"]

palabras_clave_evitar = ["tema","0","1","2","3","4","5","6","7","8","9"]

# Path to the data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# Iterate through each folder in the data directory
for folder in os.listdir(DATA_DIR):
    folder_path = os.path.join(DATA_DIR, folder)
    if os.path.isdir(folder_path):
        json_path = os.path.join(folder_path, 'guía_docente.json')
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                guia_docente = json.load(f)

            terminos_busqueda = []

            for seccion in secciones_importantes:
                if seccion in guia_docente:

                    if seccion == "programa_de_contenidos_teóricos_y_prácticos":
                        print(f"Omitiendo sección extensa: {seccion}")
                        continue

                    print(f"Procesando sección: {seccion}")
                    contenido = guia_docente[seccion]

                    for item in contenido:
                        item = item.lower()
                        regex_pattern = '|'.join(map(re.escape, separadores))
                        items = re.split(regex_pattern,item)

                        for query in items:
                            query = query.strip()
                            if len(query) < 5 or len(query) > 50:
                                continue
                            if any(bad in query for bad in palabras_clave_evitar):
                                continue
                            terminos_busqueda.append(query)

                    
                    print(terminos_busqueda)
                    #Descargar artículos de Wikipedia para los términos encontrados
                    if terminos_busqueda:
                        save_wikipedia_articles(terminos_busqueda, output_dir=folder_path, lang='es')
