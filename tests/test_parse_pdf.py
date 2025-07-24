import os
import sys
import pdfplumber

# Add the project root to the Python path to allow for absolute imports.
# This makes the script runnable from anywhere.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../app/RAG'))
sys.path.insert(0, project_root)

from populate_database import clean_text
data_path = "../data"
output_dir = "parsed_outputDoclings"


from langchain_community.document_loaders import UnstructuredFileLoader
from docling.document_converter import DocumentConverter


def main():
    """
    Processes all PDF files in the data directory, cleans their text content,
    and saves the output to text files for review.
    """
    # Create the main output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Directorio de salida creado: {output_dir}")

    # Iterate through subject folders in the data directory
    subjects = [
        folder
        for folder in os.listdir(data_path)
        if os.path.isdir(os.path.join(data_path, folder))
    ]

    if not subjects:
        print(f"⚠️ No se encontraron carpetas de asignaturas en '{data_path}'")
        return

    for subject in subjects:
        subject_path = os.path.join(data_path, subject)
        subject_output_path = os.path.join(output_dir, subject)

        # Create a subdirectory for the subject in the output directory
        if not os.path.exists(subject_output_path):
            os.makedirs(subject_output_path)

        print(f"\n📚 Procesando asignatura: {subject}")

        for filename in os.listdir(subject_path):
            if filename.lower().endswith(".pdf"):
                print(f"  🔍 Procesando archivo: {filename}")
                file_path = os.path.join(subject_path, filename)
                output_txt_path = os.path.join(
                    subject_output_path, f"{os.path.splitext(filename)[0]}.txt"
                )

                full_cleaned_text = ""

                try:

                    converter = DocumentConverter()
                    result = converter.convert(file_path)
                    full_cleaned_text = result.document.export_to_markdown()  # output: "## Docling Technical Report[...]"

                    # loader = UnstructuredFileLoader(file_path)
                    # documents = loader.load()
                    # print(len(documents))
                    # full_cleaned_text = documents[0].page_content

                    # with pdfplumber.open(file_path) as pdf:
                    #     for page_num, page in enumerate(pdf.pages):
                    #         text = page.extract_text()
                    #         if text:
                    #             cleaned_text = clean_text(text)
                    #             full_cleaned_text += (
                    #                 f"--- Página {page_num + 1} ---\n{cleaned_text}\n\n"
                    #             )

                    # Save the full cleaned text to a file
                    with open(output_txt_path, "w", encoding="utf-8") as f:
                        f.write(full_cleaned_text)
                    print(f"  ✅ Texto parseado guardado en: {output_txt_path}")

                except Exception as e:
                    print(f"  ❌ Error al procesar {filename}: {str(e)}")

if __name__ == "__main__":
    main()