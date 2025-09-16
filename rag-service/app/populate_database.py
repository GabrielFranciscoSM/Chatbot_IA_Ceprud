#!/usr/bin/env python3
"""
Script de población masiva de base de datos RAG desde directorio de archivos local
Versión migrada al RAG Service - Funciona tanto local como remoto
"""
import argparse
import os
import requests
from pathlib import Path
from typing import List, Optional
import sys

# Configuración
DEFAULT_RAG_SERVICE_URL = "http://localhost:8082"

script_dir = Path(__file__).parent.absolute()

DEFAULT_DATA_PATH = Path.joinpath(script_dir,"data")  # Para uso dentro del contenedor

class RAGDatabasePopulator:
    """Clase para poblar la base de datos RAG masivamente"""
    
    def __init__(self, rag_service_url: str = DEFAULT_RAG_SERVICE_URL):
        self.rag_service_url = rag_service_url
        
    def check_rag_service(self) -> bool:
        """Verificar que el RAG Service esté disponible"""
        try:
            response = requests.get(f"{self.rag_service_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error conectando al RAG Service: {e}")
            return False
    
    def get_supported_files(self, subject_dir: Path) -> List[Path]:
        """Obtener archivos soportados (TXT y PDF) de un directorio"""
        supported_extensions = ['.txt', '.pdf']
        files = []
        
        for ext in supported_extensions:
            files.extend(subject_dir.glob(f"*{ext}"))
        
        return sorted(files)
    
    def populate_subject(self, subject_name: str, files: List[Path], reset: bool = True) -> bool:
        """Poblar una asignatura usando el RAG Service"""
        if not files:
            print(f"  ⚠️  No se encontraron archivos soportados en {subject_name}")
            return False
        
        print(f"  📄 Archivos encontrados: {len(files)}")
        for file in files:
            print(f"    - {file.name} ({file.stat().st_size} bytes)")
        
        # Preparar archivos para upload
        request_files = []
        try:
            for file_path in files:
                content_type = 'application/pdf' if file_path.suffix == '.pdf' else 'text/plain'
                request_files.append(
                    ('files', (file_path.name, open(file_path, 'rb'), content_type))
                )
            
            # Datos del formulario
            data = {
                'subject': subject_name,
                'reset': str(reset).lower()
            }
            
            print(f"  🔄 Enviando {len(request_files)} archivos al RAG Service...")
            
            # Hacer petición con timeout largo para archivos grandes
            response = requests.post(
                f"{self.rag_service_url}/populate",
                files=request_files,
                data=data,
                timeout=600  # 10 minutos para archivos grandes
            )
            
            if response.status_code == 200:
                result = response.json()
                chunks_added = result.get('chunks_added', 0)
                existing_chunks = result.get('existing_chunks', 0)
                processed_files = result.get('processed_files', [])
                failed_files = result.get('failed_files', [])
                
                print(f"  ✅ {subject_name} poblada exitosamente")
                print(f"    📊 Chunks añadidos: {chunks_added}")
                print(f"    📊 Chunks existentes: {existing_chunks}")
                print(f"    📊 Archivos procesados: {len(processed_files)}")
                
                if failed_files:
                    print(f"    ⚠️  Archivos fallidos: {len(failed_files)}")
                    for failed in failed_files:
                        print(f"      - {failed.get('filename', 'Unknown')}: {failed.get('error', 'Unknown error')}")
                
                return True
            else:
                print(f"  ❌ Error poblando {subject_name}: HTTP {response.status_code}")
                try:
                    error_detail = response.json().get('detail', response.text)
                    print(f"      Detalle: {error_detail}")
                except:
                    print(f"      Respuesta: {response.text}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error procesando {subject_name}: {str(e)}")
            return False
        finally:
            # Cerrar archivos
            for file_tuple in request_files:
                try:
                    file_tuple[1][1].close()
                except:
                    pass
    
    def populate_from_directory(self, data_path: str, reset: bool = True, subjects: Optional[List[str]] = None) -> None:
        """Poblar todas las asignaturas desde un directorio"""
        data_dir = Path(data_path)
        
        if not data_dir.exists():
            print(f"❌ Directorio de datos no encontrado: {data_path}")
            return
        
        # Obtener directorios de asignaturas
        subject_dirs = [d for d in data_dir.iterdir() if d.is_dir()]
        
        # Filtrar asignaturas si se especifica
        if subjects:
            subject_dirs = [d for d in subject_dirs if d.name in subjects]
        
        if not subject_dirs:
            print("❌ No se encontraron directorios de asignaturas")
            return
        
        print(f"📚 Asignaturas a procesar: {[d.name for d in subject_dirs]}")
        
        # Procesar cada asignatura
        success_count = 0
        for subject_dir in subject_dirs:
            subject_name = subject_dir.name
            print(f"\n📖 Procesando asignatura: {subject_name}")
            
            files = self.get_supported_files(subject_dir)
            
            if self.populate_subject(subject_name, files, reset):
                success_count += 1
        
        print(f"\n🎉 Población completada")
        print(f"✅ Asignaturas procesadas exitosamente: {success_count}/{len(subject_dirs)}")
        
        # Verificar resultado final
        self.list_subjects()
    
    def list_subjects(self) -> None:
        """Listar asignaturas disponibles en el RAG Service"""
        try:
            response = requests.get(f"{self.rag_service_url}/subjects")
            if response.status_code == 200:
                subjects = response.json().get('subjects', [])
                print(f"📋 Asignaturas disponibles en RAG Service ({len(subjects)}): {subjects}")
            else:
                print("❌ Error obteniendo lista de asignaturas")
        except Exception as e:
            print(f"❌ Error verificando asignaturas: {str(e)}")
    
    def clear_subject(self, subject_name: str) -> bool:
        """Limpiar base de datos de una asignatura específica"""
        try:
            response = requests.delete(f"{self.rag_service_url}/subjects/{subject_name}")
            if response.status_code == 200:
                print(f"✅ Base de datos de {subject_name} limpiada")
                return True
            else:
                print(f"❌ Error limpiando {subject_name}: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error limpiando {subject_name}: {str(e)}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Poblar base de datos RAG desde directorio de archivos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Poblar todas las asignaturas desde directorio por defecto
  python populate_database.py --reset
  
  # Poblar asignaturas específicas
  python populate_database.py --subjects metaheuristicas estadistica
  
  # Poblar desde directorio personalizado
  python populate_database.py --data-path /ruta/a/datos --reset
  
  # Usar RAG Service remoto
  python populate_database.py --rag-url http://remote:8082 --reset
  
  # Solo listar asignaturas disponibles
  python populate_database.py --list-only
        """
    )
    
    parser.add_argument(
        "--data-path", 
        default=DEFAULT_DATA_PATH,
        help=f"Ruta al directorio de datos (por defecto: {DEFAULT_DATA_PATH})"
    )
    parser.add_argument(
        "--rag-url", 
        default=DEFAULT_RAG_SERVICE_URL,
        help=f"URL del RAG Service (por defecto: {DEFAULT_RAG_SERVICE_URL})"
    )
    parser.add_argument(
        "--reset", 
        action="store_true",
        help="Borrar base de datos existente antes de poblar"
    )
    parser.add_argument(
        "--subjects", 
        nargs="+",
        help="Asignaturas específicas a procesar (por defecto: todas)"
    )
    parser.add_argument(
        "--list-only", 
        action="store_true",
        help="Solo listar asignaturas disponibles sin poblar"
    )
    parser.add_argument(
        "--clear-subject",
        help="Limpiar base de datos de una asignatura específica"
    )
    
    args = parser.parse_args()
    
    # Determinar ruta de datos
    if args.data_path:
        data_path = args.data_path
    elif os.path.exists(DEFAULT_DATA_PATH):
        data_path = DEFAULT_DATA_PATH
    else:
        print(f"❌ No se encontró directorio de datos. Especifica con --data-path")
        sys.exit(1)
    
    print("🚀 RAG Database Populator")
    print(f"📁 Directorio de datos: {data_path}")
    print(f"🌐 RAG Service: {args.rag_url}")
    print("=" * 70)
    
    # Crear populator
    populator = RAGDatabasePopulator(args.rag_url)
    
    # Verificar RAG Service
    if not populator.check_rag_service():
        print("❌ RAG Service no está disponible")
        sys.exit(1)
    print("✅ RAG Service disponible")
    
    # Ejecutar acción solicitada
    if args.list_only:
        populator.list_subjects()
    elif args.clear_subject:
        populator.clear_subject(args.clear_subject)
    else:
        populator.populate_from_directory(
            data_path=data_path,
            reset=args.reset,
            subjects=args.subjects
        )


if __name__ == "__main__":
    main()
