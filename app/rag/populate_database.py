import argparse
import os
import shutil
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownTextSplitter
from langchain.schema.document import Document
from langchain_chroma import Chroma
from rag.get_embedding_function import get_embedding_function

from docling.document_converter import DocumentConverter

from dotenv import load_dotenv

load_dotenv()
# --- Configuration and Shared State ---
BASE_CHROMA_PATH = os.getenv("BASE_CHROMA_PATH", "chroma")
DATA_PATH = os.getenv("BASE_DATA_PATH","data")

def main():
    # Configurar argumentos
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Borrar y recrear la base de datos.")
    args = parser.parse_args()

    # Listar todas las carpetas de asignaturas en el directorio de datos
    subjects = [folder for folder in os.listdir(DATA_PATH) if os.path.isdir(os.path.join(DATA_PATH, folder))]
    print(f"📁 Asignaturas encontradas: {', '.join(subjects)}")

    for subject in subjects:
        chroma_path = os.path.join(BASE_CHROMA_PATH, subject)
        data_subject_path = os.path.join(DATA_PATH, subject)

        clear_database(chroma_path)#COMPROBAR FUNCIONAMIENTO ARGUMENTO

        if args.reset:
            print(f"✨ Borrando base de datos para {subject}")
            clear_database(chroma_path)

        print(f"\n📚 Procesando asignatura: {subject}")
        documents = load_documents(data_subject_path)
        if not documents:
            print(f"⚠️ No hay documentos válidos para {subject}")
            continue

        print(f"\n📚 Creando Chunks de asignatura: {subject}")
        chunks = split_documents(documents)
        print(f"\n📚 Añadiendo la asignatura a la base de datos: {subject}")
        add_to_chroma(chunks, chroma_path)

import re

def clean_text(text):
    """
    Limpieza robusta para textos académicos y técnicos, evitando eliminar contenido relevante y conservando saltos de línea dobles como separación de párrafos.
    """
    import re
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

def load_documents(data_path):
    valid_documents = []
    for filename in os.listdir(data_path):
        
        if filename.endswith(".pdf"):
            print(f"🔍 Procesando archivo: {filename}")
            file_path = os.path.join(data_path, filename)
            try:                
                converter = DocumentConverter()
                result = converter.convert(file_path)
                text = result.document.export_to_markdown()
                c_text = clean_text(text)

                valid_documents.append(
                    Document(
                        page_content=c_text,
                        metadata={
                            "source": filename.split(".")[0],
                            "subject": data_path.split("/")[-1]
                        }
                    )
                )             
                # with pdfplumber.open(file_path) as pdf:
                #     for page_num, page in enumerate(pdf.pages):
                #         text = page.extract_text()
                #         if text:
                #             cleaned_text = clean_text(text)
                #             print("DOCUMENTO: " + filename + "\n CONTENIDO: \n" + cleaned_text + "\n")
                #             valid_documents.append(
                #                 Document(
                #                     page_content=cleaned_text,
                #                     metadata={
                #                         "source": filename,
                #                         "page": page_num,
                #                         "subject": data_path.split("/")[-1]
                #                     }
                #                 )
                #             )
            except Exception as e:
                print(f"❌ Error al procesar {filename}: {str(e)}")
    return valid_documents

def split_documents(documents):
    """Dividir texto en fragmentos con parámetros optimizados."""


    # headers_to_split_on = [
    #     ("#", "Header 1"),
    #     ("##", "Header 2"),
    # ]

    # MD splits
    markdown_splitter = MarkdownTextSplitter(
        chunk_size=500,          # Tamaño reducido para mayor precisión
        chunk_overlap=50,        # Overlap para mantener coherencia
        length_function=len
    )
    #header_md_split = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on, strip_headers=False)
    md_header_splits = markdown_splitter.split_documents(documents)

    # text_splitter = RecursiveCharacterTextSplitter(
    #     chunk_size=3000,          # Tamaño reducido para mayor precisión
    #     chunk_overlap=300,        # Overlap para mantener coherencia
    #     separators=["\n\n", "\n", ". ", " ", ""],  # Jerarquía de separadores
    #     length_function=len
    # )
    # recursive_splits = text_splitter.split_documents(documents)

    return md_header_splits 

    
def add_to_chroma(chunks, chroma_path):
    """Actualizar base de datos Chroma con chunks en lotes (batches)."""
    if not chunks:
        print("ℹ️ No hay chunks para procesar.")
        return

    db = Chroma(
        persist_directory=chroma_path,
        embedding_function=get_embedding_function()
    )

    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])
    print(f"📄 Documentos existentes en la DB: {len(existing_ids)}")

    new_chunks = []
    for i, chunk in enumerate(chunks):
        # Generar un ID único para cada chunk
        chunk_id = f"{chunk.metadata['source']}-{i}"
        
        if chunk_id not in existing_ids:
            # Asignar el ID al metadata para que LangChain lo use
            chunk.metadata["id"] = chunk_id
            new_chunks.append(chunk)

    if not new_chunks:
        print("✅ No hay nuevos documentos para añadir.")
        return

    # --- INICIO DE LA MODIFICACIÓN CLAVE ---
    
    # Procesar en lotes para no sobrecargar el servidor de embeddings
    batch_size = 8  # Puedes ajustar este valor. Empieza con algo pequeño.
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

    print("✅ Todos los nuevos chunks han sido añadidos exitosamente.")
    # --- FIN DE LA MODIFICACIÓN CLAVE ---

  

def clear_database(chroma_path):
    """Borrar base de datos existente."""
    if os.path.exists(chroma_path):
        shutil.rmtree(chroma_path)
        print(f"🗑️ Base de datos eliminada: {chroma_path}")

if __name__ == "__main__":
    main()