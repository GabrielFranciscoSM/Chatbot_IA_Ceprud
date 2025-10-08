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
    
    def parse_profesorado_and_tutorias(self, soup) -> List[Dict[str, Any]]:
        """
        Parsea las secciones de profesorado y tutorías de la nueva estructura UGR
        """
        profesores_data = {}
        
        # Encontrar la sección de Profesorado
        profesorado_header = None
        for h2 in soup.find_all('h2'):
            if h2.get_text(strip=True) == 'Profesorado':
                profesorado_header = h2
                break
        
        if profesorado_header:
            # Buscar subsecciones (Teórico, Práctico, etc.)
            current_element = profesorado_header.find_next_sibling()
            while current_element and current_element.name != 'h2':
                if current_element.name == 'h3':
                    role = current_element.get_text(strip=True)
                    # Buscar lista de profesores para este rol
                    list_element = current_element.find_next_sibling()
                    while list_element and list_element.name not in ['h2', 'h3'] and list_element.name != 'ul':
                        list_element = list_element.find_next_sibling()
                    
                    if list_element and list_element.name == 'ul':
                        for li in list_element.find_all('li'):
                            text = li.get_text(strip=True)
                            # Limpiar texto
                            text = re.sub(r'\s+', ' ', text)
                            
                            if '. Grupo' in text:
                                parts = text.split('. Grupo')
                                nombre = parts[0].strip()
                                grupos_text = parts[1].strip()
                                # Extraer grupos
                                grupos_match = re.search(r':\s*(.+)', grupos_text)
                                grupos = grupos_match.group(1).strip() if grupos_match else ""
                            elif ' Grupo' in text:
                                # Caso sin punto: "Nombre Grupo: X"
                                parts = text.split(' Grupo')
                                nombre = parts[0].strip()
                                grupos_text = parts[1].strip()
                                # Extraer grupos
                                grupos_match = re.search(r'(?:s)?:\s*(.+)', grupos_text)
                                grupos = grupos_match.group(1).strip() if grupos_match else ""
                            else:
                                # Formato simple: "Nombre"
                                nombre = text.strip()
                                grupos = ""
                            
                            if nombre:
                                # Normalizar nombre (limpiar espacios extras)
                                nombre = re.sub(r'\s+', ' ', nombre)
                                
                                if nombre not in profesores_data:
                                    profesores_data[nombre] = {'nombre': nombre}
                                profesores_data[nombre]['rol'] = role
                                if grupos:
                                    profesores_data[nombre]['grupos'] = grupos
                
                current_element = current_element.find_next_sibling()
        
        # Encontrar la sección de Tutorías
        tutorias_header = None
        for h2 in soup.find_all('h2'):
            if h2.get_text(strip=True) == 'Tutorías':
                tutorias_header = h2
                break
        
        if tutorias_header:
            current_element = tutorias_header.find_next_sibling()
            while current_element and current_element.name != 'h2':
                if current_element.name == 'h3':
                    nombre_profesor = current_element.get_text(strip=True)
                    # Limpiar nombre
                    nombre_profesor = re.sub(r'\s+', ' ', nombre_profesor)
                    
                    # Encontrar el contenido de las tutorías
                    tutoria_content = []
                    next_element = current_element.find_next_sibling()
                    while next_element and next_element.name not in ['h2', 'h3']:
                        if next_element.name in ['p', 'ul', 'div'] and next_element.get_text(strip=True):
                            content_text = next_element.get_text(strip=True)
                            # Limpiar espacios
                            content_text = re.sub(r'\s+', ' ', content_text)
                            tutoria_content.append(content_text)
                        next_element = next_element.find_next_sibling()
                    
                    # Buscar al profesor en los datos existentes (por nombre exacto o similar)
                    found_professor = None
                    for existing_name in profesores_data.keys():
                        if nombre_profesor == existing_name or self._similar_names(nombre_profesor, existing_name):
                            found_professor = existing_name
                            break
                    
                    tutoria_text = ' '.join(tutoria_content)
                    if found_professor:
                        profesores_data[found_professor]['tutorias'] = tutoria_text
                    else:
                        # Si no existe, crear entrada solo con tutorías
                        profesores_data[nombre_profesor] = {
                            'nombre': nombre_profesor,
                            'tutorias': tutoria_text
                        }
                
                current_element = current_element.find_next_sibling()
        
        return list(profesores_data.values())
    
    def _similar_names(self, name1: str, name2: str) -> bool:
        """
        Compara si dos nombres son similares (para casos donde el formato cambia ligeramente)
        """
        # Extraer solo palabras alfabéticas (ignorar puntos, etc.)
        words1 = set(re.findall(r'\b[A-Za-záéíóúüñ]+\b', name1.lower()))
        words2 = set(re.findall(r'\b[A-Za-záéíóúüñ]+\b', name2.lower()))
        
        # Si hay al menos 2 palabras en común, consideramos que son el mismo profesor
        return len(words1.intersection(words2)) >= 2
    
    def parse_section_by_header(self, soup, header_text: str) -> Optional[Any]:
        """
        Busca una sección por su header h2 y extrae su contenido
        """
        header = None
        for h2 in soup.find_all('h2'):
            if header_text.lower() in h2.get_text(strip=True).lower():
                header = h2
                break
        
        if not header:
            return None
        
        content = []
        current_element = header.find_next_sibling()
        
        while current_element and current_element.name != 'h2':
            if current_element.name == 'h3':
                # Es una subsección
                subsection_title = current_element.get_text(strip=True)
                subsection_content = []
                
                next_element = current_element.find_next_sibling()
                while next_element and next_element.name not in ['h2', 'h3']:
                    if next_element.name == 'ul':
                        # Lista de items
                        for li in next_element.find_all('li'):
                            item_text = li.get_text(strip=True)
                            item_text = re.sub(r'\s+', ' ', item_text)  # Limpiar espacios
                            if item_text:
                                subsection_content.append(item_text)
                    elif next_element.get_text(strip=True):
                        text_content = next_element.get_text(strip=True)
                        text_content = re.sub(r'\s+', ' ', text_content)  # Limpiar espacios
                        subsection_content.append(text_content)
                    next_element = next_element.find_next_sibling()
                
                content.append({
                    'subsection': subsection_title,
                    'content': subsection_content
                })
                current_element = next_element
                continue
            
            elif current_element.name == 'ul':
                # Lista directa bajo el header
                for li in current_element.find_all('li'):
                    item_text = li.get_text(strip=True)
                    item_text = re.sub(r'\s+', ' ', item_text)  # Limpiar espacios
                    if item_text:
                        content.append(item_text)
            elif current_element.get_text(strip=True):
                text_content = current_element.get_text(strip=True)
                text_content = re.sub(r'\s+', ' ', text_content)  # Limpiar espacios
                content.append(text_content)
            
            current_element = current_element.find_next_sibling()
        
        return content if content else None

    def extract_basic_info(self, soup) -> Dict[str, str]:
        """
        Extrae información básica de la guía docente (grado, rama, módulo, etc.)
        """
        info = {}
        
        # Mapeo de campos básicos
        basic_fields = [
            'Grado', 'Rama', 'Módulo', 'Materia', 'Curso', 
            'Semestre', 'Créditos', 'Tipo'
        ]
        
        for field in basic_fields:
            header = None
            for h2 in soup.find_all('h2'):
                if h2.get_text(strip=True) == field:
                    header = h2
                    break
            
            if header:
                # Buscar el contenido después del header
                next_element = header.find_next_sibling()
                while next_element and next_element.name != 'h2':
                    text = next_element.get_text(strip=True)
                    if text:
                        info[field.lower()] = text
                        break
                    next_element = next_element.find_next_sibling()
        
        return info
    
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
                guia_data['asignatura'] = title_tag.get_text(strip=True)
            
            # Extraer información básica
            basic_info = self.extract_basic_info(soup)
            guia_data.update(basic_info)
            
            # Extraer profesorado y tutorías
            guia_data['profesorado_y_tutorias'] = self.parse_profesorado_and_tutorias(soup)
            
            # Mapeo de secciones por header
            sections = {
                'prerrequisitos_o_recomendaciones': 'Prerrequisitos',
                'breve_descripción_de_contenidos': 'Breve descripción de contenidos',
                'competencias': 'Competencias',
                'resultados_de_aprendizaje': 'Resultados de aprendizaje',
                'programa_de_contenidos_teóricos_y_prácticos': 'Programa de contenidos',
                'bibliografía': 'Bibliografía',
                'enlaces_recomendados': 'Enlaces recomendados',
                'metodología_docente': 'Metodología docente',
                'evaluación': 'Evaluación',
                'software_libre': 'Software Libre'
            }
            
            # Extraer cada sección
            for key, header_text in sections.items():
                content = self.parse_section_by_header(soup, header_text)
                if content:
                    guia_data[key] = self._format_section_content(content, key)
            
            print(f"✅ Guía docente extraída: {guia_data.get('asignatura', 'Sin título')}")
            return guia_data
            
        except Exception as e:
            print(f"❌ Error extrayendo guía docente de {url}: {e}")
            return {}
    
    def _format_section_content(self, content: List, section_key: str) -> Any:
        """
        Formatea el contenido de una sección según su tipo
        """
        if section_key == 'competencias':
            # Formatear competencias con subsecciones
            competencias = {}
            for item in content:
                if isinstance(item, dict) and 'subsection' in item:
                    key = item['subsection'].lower().replace(' ', '_')
                    competencias[key] = item['content']
                elif isinstance(item, str):
                    if 'general_competences' not in competencias:
                        competencias['general_competences'] = []
                    competencias['general_competences'].append(item)
            return competencias
        
        elif section_key == 'programa_de_contenidos_teóricos_y_prácticos':
            # Formatear programa con teórico y práctico
            programa = {}
            for item in content:
                if isinstance(item, dict) and 'subsection' in item:
                    key = item['subsection'].lower()
                    if 'teórico' in key:
                        # Formatear temas separando por "Tema X"
                        temas = []
                        for tema_text in item['content']:
                            # Dividir por "Tema" seguido de número
                            tema_parts = re.split(r'(?=Tema\s+\d+)', tema_text)
                            for parte in tema_parts:
                                parte = parte.strip()
                                if parte and parte.startswith('Tema'):
                                    # Limpiar el tema
                                    tema_clean = re.sub(r'\.$', '', parte.strip())
                                    temas.append({
                                        'tema': tema_clean,
                                        'puntos': []
                                    })
                        programa['teórico'] = temas
                    elif 'práctico' in key:
                        # Formatear prácticas separando por "Práctica X" o "Seminario"
                        practicas = []
                        for practica_text in item['content']:
                            # Dividir por "Práctica" o "Seminario"
                            practica_parts = re.split(r'(?=(?:Práctica|Seminario)\s+(?:\d+|práctico))', practica_text)
                            for parte in practica_parts:
                                parte = parte.strip()
                                if parte and (parte.startswith('Práctica') or parte.startswith('Seminario')):
                                    # Limpiar la práctica
                                    practica_clean = re.sub(r'\.$', '', parte.strip())
                                    practicas.append(practica_clean)
                        programa['práctico'] = practicas
            return programa
        
        elif section_key == 'bibliografía':
            # Formatear bibliografía con subsecciones
            bibliografia = {}
            for item in content:
                if isinstance(item, dict) and 'subsection' in item:
                    key = item['subsection'].lower().replace(' ', '_')
                    bibliografia[key] = item['content']
            return bibliografia
        
        elif section_key == 'evaluación':
            # Formatear evaluación con tipos
            evaluacion = {}
            for item in content:
                if isinstance(item, dict) and 'subsection' in item:
                    key = item['subsection'].lower().replace(' ', '_')
                    evaluacion[key] = item['content']
            return evaluacion
        
        else:
            # Para otras secciones, devolver lista simple separando por puntos cuando sea apropiado
            result = []
            for item in content:
                if isinstance(item, dict) and 'content' in item:
                    result.extend(item['content'])
                elif isinstance(item, str):
                    # Si el texto contiene múltiples elementos separados por puntos, separarlos
                    if section_key in ['breve_descripción_de_contenidos', 'resultados_de_aprendizaje', 'metodología_docente']:
                        # Dividir por puntos seguidos de mayúscula o por patrones específicos
                        if section_key == 'metodología_docente':
                            # Para metodología, dividir por MD\d\d completo (no solo el prefijo)
                            parts = re.split(r'(?=MD\d+\.\s*[A-Z])', item)
                        elif section_key == 'resultados_de_aprendizaje':
                            # Para resultados, dividir por puntos seguidos de mayúscula
                            parts = re.split(r'\.(?=[A-ZÁÉÍÓÚÜÑ])', item)
                        else:
                            # Para descripción de contenidos, dividir por puntos seguidos de mayúscula
                            parts = re.split(r'\.(?=[A-ZÁÉÍÓÚÜÑ])', item)
                        
                        for part in parts:
                            part = part.strip()
                            if part:
                                # Restaurar el punto final si se perdió
                                if not part.endswith('.') and section_key != 'metodología_docente':
                                    part += '.'
                                result.append(part)
                    else:
                        result.append(item)
            return result
    
    def convert_guia_to_text(self, guia_data: Dict[str, Any]) -> str:
        """Convertir datos de guía docente a texto estructurado para RAG"""
        if not guia_data:
            return ""
        
        text_parts = []
        
        # Título
        if 'asignatura' in guia_data:
            text_parts.append(f"# {guia_data['asignatura']}\n")
        
        # Información básica
        basic_fields = ['grado', 'rama', 'módulo', 'materia', 'curso', 'semestre', 'créditos', 'tipo']
        for field in basic_fields:
            if field in guia_data:
                text_parts.append(f"**{field.title()}**: {guia_data[field]}")
        text_parts.append("")
        
        # Profesorado y tutorías
        if 'profesorado_y_tutorias' in guia_data and guia_data['profesorado_y_tutorias']:
            text_parts.append("## Profesorado y Tutorías")
            for profesor in guia_data['profesorado_y_tutorias']:
                if isinstance(profesor, dict):
                    text_parts.append(f"**{profesor.get('nombre', 'Sin nombre')}**")
                    if 'rol' in profesor:
                        text_parts.append(f"- Rol: {profesor['rol']}")
                    if 'grupos' in profesor:
                        text_parts.append(f"- Grupos: {profesor['grupos']}")
                    if 'tutorias' in profesor:
                        text_parts.append(f"- Tutorías: {profesor['tutorias']}")
                    text_parts.append("")
        
        # Prerrequisitos
        if 'prerrequisitos_o_recomendaciones' in guia_data and guia_data['prerrequisitos_o_recomendaciones']:
            text_parts.append("## Prerrequisitos y Recomendaciones")
            self._format_content(text_parts, guia_data['prerrequisitos_o_recomendaciones'])
            text_parts.append("")
        
        # Breve descripción de contenidos
        if 'breve_descripción_de_contenidos' in guia_data and guia_data['breve_descripción_de_contenidos']:
            text_parts.append("## Breve Descripción de Contenidos")
            self._format_content(text_parts, guia_data['breve_descripción_de_contenidos'])
            text_parts.append("")
        
        # Competencias
        if 'competencias' in guia_data and guia_data['competencias']:
            text_parts.append("## Competencias")
            if isinstance(guia_data['competencias'], dict):
                for key, value in guia_data['competencias'].items():
                    text_parts.append(f"### {key.replace('_', ' ').title()}")
                    if isinstance(value, list):
                        for item in value:
                            text_parts.append(f"- {item}")
                    else:
                        text_parts.append(str(value))
                    text_parts.append("")
            else:
                self._format_content(text_parts, guia_data['competencias'])
                text_parts.append("")
        
        # Resultados de aprendizaje
        if 'resultados_de_aprendizaje' in guia_data and guia_data['resultados_de_aprendizaje']:
            text_parts.append("## Resultados de Aprendizaje")
            self._format_content(text_parts, guia_data['resultados_de_aprendizaje'])
            text_parts.append("")
        
        # Programa de contenidos
        if 'programa_de_contenidos_teóricos_y_prácticos' in guia_data and guia_data['programa_de_contenidos_teóricos_y_prácticos']:
            text_parts.append("## Programa de Contenidos Teóricos y Prácticos")
            programa = guia_data['programa_de_contenidos_teóricos_y_prácticos']
            if isinstance(programa, dict):
                if 'teórico' in programa:
                    text_parts.append("### Teórico")
                    for tema in programa['teórico']:
                        if isinstance(tema, dict) and 'tema' in tema:
                            text_parts.append(f"- {tema['tema']}")
                        else:
                            text_parts.append(f"- {tema}")
                    text_parts.append("")
                if 'práctico' in programa:
                    text_parts.append("### Práctico")
                    for practica in programa['práctico']:
                        text_parts.append(f"- {practica}")
                    text_parts.append("")
            else:
                self._format_content(text_parts, programa)
                text_parts.append("")
        
        # Bibliografía
        if 'bibliografía' in guia_data and guia_data['bibliografía']:
            text_parts.append("## Bibliografía")
            if isinstance(guia_data['bibliografía'], dict):
                for key, value in guia_data['bibliografía'].items():
                    text_parts.append(f"### {key.replace('_', ' ').title()}")
                    if isinstance(value, list):
                        for item in value:
                            text_parts.append(f"- {item}")
                    else:
                        text_parts.append(str(value))
                    text_parts.append("")
            else:
                self._format_content(text_parts, guia_data['bibliografía'])
                text_parts.append("")
        
        # Enlaces recomendados
        if 'enlaces_recomendados' in guia_data and guia_data['enlaces_recomendados']:
            text_parts.append("## Enlaces Recomendados")
            self._format_content(text_parts, guia_data['enlaces_recomendados'])
            text_parts.append("")
        
        # Metodología docente
        if 'metodología_docente' in guia_data and guia_data['metodología_docente']:
            text_parts.append("## Metodología Docente")
            self._format_content(text_parts, guia_data['metodología_docente'])
            text_parts.append("")
        
        # Evaluación
        if 'evaluación' in guia_data and guia_data['evaluación']:
            text_parts.append("## Evaluación")
            if isinstance(guia_data['evaluación'], dict):
                for key, value in guia_data['evaluación'].items():
                    text_parts.append(f"### {key.replace('_', ' ').title()}")
                    if isinstance(value, list):
                        for item in value:
                            text_parts.append(f"- {item}")
                    else:
                        text_parts.append(str(value))
                    text_parts.append("")
            else:
                self._format_content(text_parts, guia_data['evaluación'])
                text_parts.append("")
        
        # Software libre
        if 'software_libre' in guia_data and guia_data['software_libre']:
            text_parts.append("## Software Libre")
            self._format_content(text_parts, guia_data['software_libre'])
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
                        if 'puntos' in item and item['puntos']:
                            for punto in item['puntos']:
                                text_parts.append(f"- {punto}")
                    elif 'texto' in item:  # Es un item con enlace
                        text_parts.append(f"- {item['texto']}")
                        if 'enlace' in item:
                            text_parts.append(f"  Enlace: {item['enlace']}")
                    else:
                        # Diccionario genérico
                        for key, value in item.items():
                            text_parts.append(f"**{key}**: {value}")
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
