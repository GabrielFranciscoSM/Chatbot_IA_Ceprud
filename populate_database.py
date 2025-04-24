import argparse
import os
import shutil
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_chroma import Chroma
from get_embedding_function import get_embedding_function
import pdfplumber

BASE_CHROMA_PATH = "chroma"
DATA_PATH = "data"

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

        if args.reset:
            print(f"✨ Borrando base de datos para {subject}")
            clear_database(chroma_path)

        print(f"\n📚 Procesando asignatura: {subject}")
        documents = load_documents(data_subject_path)
        if not documents:
            print(f"⚠️ No hay documentos válidos para {subject}")
            continue

        chunks = split_documents(documents)
        add_to_chroma(chunks, chroma_path)

import re

def clean_text(text):
    """
    Realiza una limpieza exhaustiva del texto para prepararlo para el procesamiento.
    
    Args:
        text (str): Texto a limpiar.
    
    Returns:
        str: Texto limpio y normalizado.
    """
    # 1. Eliminar encabezados y pies de página comunes
    text = re.sub(r"^\s*[\w\s\-\.,]+\n+", "", text, flags=re.MULTILINE)  # Encabezados
    text = re.sub(r"\n\s*[\w\s\-\.,]+$", "", text, flags=re.MULTILINE)  # Pies de página
    
    # 2. Eliminar números de página y patrones similares
    text = re.sub(r"\b\d{1,3}\b\s*$", "", text, flags=re.MULTILINE)  # Números solitarios al final de líneas
    
    # 3. Eliminar saltos de línea excesivos
    text = re.sub(r"\n{2,}", "\n\n", text)  # Reducir múltiples saltos de línea a dos
    
    # 4. Eliminar caracteres especiales no deseados
    text = re.sub(r"[^\w\sáéíóúüñÁÉÍÓÚÜÑ\.,;:\-\(\)\[\]\{\}¡!¿?\"\'/]", "", text)  # Mantener solo caracteres útiles
    
    # 5. Normalizar espacios en blanco
    text = re.sub(r"\s+", " ", text)  # Reducir múltiples espacios a uno solo
    text = re.sub(r"^\s+|\s+$", "", text)  # Eliminar espacios al inicio y al final
    
    # 6. Eliminar contenido irrelevante como notas al pie o metadatos
    text = re.sub(r"^\s*Nota\s*:.*$", "", text, flags=re.MULTILINE)  # Notas al pie
    text = re.sub(r"^\s*Fuente\s*:.*$", "", text, flags=re.MULTILINE)  # Fuentes
    text = re.sub(r"^\s*Figura\s*\d+\s*:.*$", "", text, flags=re.MULTILINE)  # Referencias a figuras
    text = re.sub(r"^\s*Tabla\s*\d+\s*:.*$", "", text, flags=re.MULTILINE)  # Referencias a tablas
    
    # 7. Eliminar URLs y direcciones web
    text = re.sub(r"https?://[^\s]+", "", text)  # URLs
    text = re.sub(r"www\.[^\s]+", "", text)  # Direcciones web
    
    # 8. Eliminar marcas de formato HTML/XML
    text = re.sub(r"<[^>]+>", "", text)  # Etiquetas HTML/XML
    
    return text.strip()

def load_documents(data_path):
    valid_documents = []
    for filename in os.listdir(data_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(data_path, filename)
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page_num, page in enumerate(pdf.pages):
                        text = page.extract_text()
                        if text:
                            cleaned_text = clean_text(text)
                            valid_documents.append(
                                Document(
                                    page_content=cleaned_text,
                                    metadata={
                                        "source": filename,
                                        "page": page_num,
                                        "subject": data_path.split("/")[-1]
                                    }
                                )
                            )
            except Exception as e:
                print(f"❌ Error al procesar {filename}: {str(e)}")
    return valid_documents

def split_documents(documents):
    """Dividir texto en fragmentos con parámetros optimizados."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,          # Tamaño reducido para mayor precisión
        chunk_overlap=80,        # Overlap para mantener coherencia
        separators=["\n\n", "\n", ". ", " ", ""],  # Jerarquía de separadores
        length_function=len
    )
    return text_splitter.split_documents(documents)

def add_to_chroma(chunks, chroma_path):
    """Actualizar base de datos Chroma con chunks."""
    if not chunks:
        return

    db = Chroma(
        persist_directory=chroma_path,
        embedding_function=get_embedding_function()
    )

    existing_items = db.get(include=[])  # IDs siempre están incluidos por defecto
    existing_ids = set(existing_items["ids"])
    print(f"Documentos existentes en la DB: {len(existing_ids)}")

    new_chunks = []
    for chunk in chunks:
        # Generar ID único basado en página y posición
        page_id = f"{chunk.metadata['source']}:{chunk.metadata['page']}"
        chunk_id = f"{page_id}:{len(new_chunks)}"
        chunk.metadata["id"] = chunk_id

        if chunk_id not in existing_ids:
            new_chunks.append(chunk)

    if new_chunks:
        print(f"👉 Insertando {len(new_chunks)} nuevos chunks")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
    else:
        print("✅ No hay nuevos documentos para añadir")

def clear_database(chroma_path):
    """Borrar base de datos existente."""
    if os.path.exists(chroma_path):
        shutil.rmtree(chroma_path)
        print(f"🗑️ Base de datos eliminada: {chroma_path}")

if __name__ == "__main__":
    main()