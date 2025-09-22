"""
Módulo para procesamiento de documentos (PDF, TXT) y población de la base de datos RAG
"""
import os
import re
import tempfile
import shutil
from typing import List, Dict, Any, Union
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from docling.document_converter import DocumentConverter
from fastapi import UploadFile

from .embeddings import get_embedding_function

# Configuración de rutas
BASE_CHROMA_PATH = os.getenv("BASE_CHROMA_PATH", "/app/data/chroma")


class DocumentProcessor:
    """Clase para procesar documentos y poblar la base de datos RAG"""
    
    def __init__(self):
        self.embedding_function = get_embedding_function()
        
    def clean_text(self, text: str) -> str:
        """
        Limpieza robusta para textos académicos y técnicos, evitando eliminar contenido relevante 
        y conservando saltos de línea dobles como separación de párrafos.
        """
        # 1. Eliminar líneas que sean solo números de página (1-3 dígitos)
        text = re.sub(r"^\s*\d{1,3}\s*$", "", text, flags=re.MULTILINE)

        # 2. Eliminar líneas que sean solo separadores o imágenes HTML/Markdown
        text = re.sub(r"^\s*[-–—_=]{3,}\s*$", "", text, flags=re.MULTILINE)  # Separadores
        text = re.sub(r"^\s*<!--.*?-->", "", text, flags=re.MULTILINE)  # Comentarios HTML
        text = re.sub(r"^\s*!\[.*?\]\(.*?\)", "", text, flags=re.MULTILINE)  # Imágenes Markdown

        # 3. Eliminar URLs y direcciones web
        text = re.sub(r"https?://[^\s]+", "", text)
        text = re.sub(r"www\.[^\s]+", "", text)

        # 4. Eliminar etiquetas HTML/XML
        text = re.sub(r"<[^>]+>", "", text)

        # 5. Eliminar notas al pie, fuentes, figuras, tablas (líneas que empiezan por esas palabras)
        text = re.sub(r"^\s*Nota\s*:.*$", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\s*Fuente\s*:.*$", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\s*Figura\s*\d+\s*:.*$", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\s*Tabla\s*\d+\s*:.*$", "", text, flags=re.MULTILINE)

        # 6. Eliminar bloques de tablas Markdown (líneas que empiezan por '|')
        text = re.sub(r"(\n\|.*?\|)+", "\n", text)

        # 7. Eliminar líneas vacías múltiples (dejar máximo dos saltos de línea consecutivos)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # 8. Normalizar espacios en blanco SOLO dentro de líneas con contenido
        text = '\n'.join([re.sub(r'([ \t]+)', ' ', line).strip() if line.strip() else '' for line in text.split('\n')])

        # 9. Eliminar caracteres de control no imprimibles, excepto salto de línea (\x0A)
        text = re.sub(r"[\x00-\x09\x0B-\x1F\x7F]", "", text)

        return text.strip()

    async def process_uploaded_file(self, file: UploadFile, subject: str) -> Document:
        """Procesar un archivo subido (PDF o TXT) y convertirlo en un Document."""
        file_content = await file.read()
        filename = file.filename or "unknown"
        
        if filename.endswith(".pdf"):
            # Crear archivo temporal para el PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                converter = DocumentConverter()
                result = converter.convert(temp_file_path)
                text = result.document.export_to_markdown()
                cleaned_text = self.clean_text(text)
            finally:
                # Limpiar archivo temporal
                os.unlink(temp_file_path)
                
        elif filename.endswith(".txt"):
            text = file_content.decode('utf-8')
            cleaned_text = self.clean_text(text)
        else:
            raise ValueError(f"Tipo de archivo no soportado: {filename}")
        
        return Document(
            page_content=cleaned_text,
            metadata={
                "source": filename.split(".")[0],
                "subject": subject,
                "filename": filename
            }
        )

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Dividir texto en fragmentos con parámetros optimizados."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=200,          # Tamaño reducido para mayor precisión
            chunk_overlap=50,        # Overlap para mantener coherencia
            separators=["\n\n", "\n", ". ", " ", ""],  # Jerarquía de separadores
            length_function=len
        )
        return text_splitter.split_documents(documents)

    def _get_chroma_path(self, subject: str) -> str:
        """Obtiene la ruta de ChromaDB para una asignatura"""
        return os.path.join(BASE_CHROMA_PATH, subject)

    def add_to_chroma(self, chunks: List[Document], subject: str) -> Dict[str, Any]:
        """Actualizar base de datos Chroma con chunks en lotes (batches)."""
        if not chunks:
            return {"message": "No hay chunks para procesar", "chunks_added": 0}

        chroma_path = self._get_chroma_path(subject)
        
        # Crear directorio si no existe
        os.makedirs(chroma_path, exist_ok=True)
        
        db = Chroma(
            persist_directory=chroma_path,
            embedding_function=self.embedding_function
        )

        existing_items = db.get(include=[])
        existing_ids = set(existing_items["ids"])
        
        new_chunks = []
        for i, chunk in enumerate(chunks):
            # Generar un ID único para cada chunk
            chunk_id = f"{chunk.metadata['source']}-{i}"
            
            if chunk_id not in existing_ids:
                # Asignar el ID al metadata para que LangChain lo use
                chunk.metadata["id"] = chunk_id
                new_chunks.append(chunk)

        if not new_chunks:
            return {
                "message": "No hay nuevos documentos para añadir", 
                "chunks_added": 0,
                "existing_chunks": len(existing_ids)
            }

        # Procesar en lotes para no sobrecargar el servidor de embeddings
        batch_size = 128
        total_new_chunks = len(new_chunks)
        
        print(f"👉 Insertando {total_new_chunks} nuevos chunks en lotes de {batch_size}...")

        for i in range(0, total_new_chunks, batch_size):
            # Obtener el lote actual de chunks
            batch = new_chunks[i:i + batch_size]
            
            # Obtener los IDs correspondientes para este lote
            batch_ids = [chunk.metadata["id"] for chunk in batch]
            
            current_batch_num = (i // batch_size) + 1
            total_batches = (total_new_chunks + batch_size - 1) // batch_size
            
            print(f"  - Procesando lote {current_batch_num}/{total_batches}...")
            
            # Añadir el lote a la base de datos
            db.add_documents(documents=batch, ids=batch_ids)

        return {
            "message": f"Se añadieron {total_new_chunks} chunks exitosamente",
            "chunks_added": total_new_chunks,
            "existing_chunks": len(existing_ids),
            "batch_size": batch_size,
            "total_batches": (total_new_chunks + batch_size - 1) // batch_size
        }
    
    def clear_database(self, subject: str) -> Dict[str, str]:
        """Borrar base de datos existente para una asignatura."""
        chroma_path = self._get_chroma_path(subject)
        if os.path.exists(chroma_path):
            shutil.rmtree(chroma_path)
            return {"message": f"Base de datos eliminada para {subject}"}
        return {"message": f"No existe base de datos para {subject}"}

    async def populate_subject_from_files(
        self, 
        files: List[UploadFile], 
        subject: str, 
        reset: bool = False
    ) -> Dict[str, Any]:
        """
        Poblar una asignatura con archivos reales (PDF/TXT).
        
        Args:
            files: Lista de archivos a procesar
            subject: Nombre de la asignatura
            reset: Si True, borra la base de datos existente antes de poblar
            
        Returns:
            Diccionario con el resultado de la operación
        """
        try:
            # Limpiar base de datos si se solicita
            if reset:
                self.clear_database(subject)
                print(f"✨ Base de datos reseteada para {subject}")

            # Procesar archivos
            documents = []
            processed_files = []
            failed_files = []

            for file in files:
                try:
                    print(f"🔍 Procesando archivo: {file.filename}")
                    document = await self.process_uploaded_file(file, subject)
                    documents.append(document)
                    processed_files.append(file.filename)
                except Exception as e:
                    print(f"❌ Error al procesar {file.filename}: {str(e)}")
                    failed_files.append({"filename": file.filename, "error": str(e)})

            if not documents:
                return {
                    "success": False,
                    "message": "No se pudieron procesar documentos válidos",
                    "processed_files": processed_files,
                    "failed_files": failed_files
                }

            # Dividir en chunks
            print(f"📚 Creando chunks para asignatura: {subject}")
            chunks = self.split_documents(documents)

            # Añadir a ChromaDB
            print(f"📚 Añadiendo a la base de datos: {subject}")
            result = self.add_to_chroma(chunks, subject)

            return {
                "success": True,
                "subject": subject,
                "processed_files": processed_files,
                "failed_files": failed_files,
                "documents_processed": len(documents),
                **result
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error general al poblar {subject}: {str(e)}",
                "processed_files": [],
                "failed_files": []
            }


# Instancia global del procesador de documentos
document_processor = DocumentProcessor()
