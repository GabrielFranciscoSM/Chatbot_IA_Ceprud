import os
import json
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch
import pdfplumber

# =====================================
# ============ CONFIGURACIÓN ==========
# =====================================
HF_TOKEN = "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"  
os.environ["HUGGINGFACEHUB_API_TOKEN"] = HF_TOKEN
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Modelos
QUESTION_MODEL = "mrm8488/t5-base-finetuned-question-generation-ap"
SUMMARIZER_MODEL = "mrm8488/bert2bert_shared-spanish-finetuned-summarization"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Funciones auxiliares
def clean_text(text):
    """Limpieza exhaustiva del texto (como en tu función original)"""
    text = re.sub(r"^\s*[\w\s\-\.,]+\n+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n\s*[\w\s\-\.,]+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\b\d{1,3}\b\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"[^\w\sáéíóúüñÁÉÍÓÚÜÑ\.,;:\-\(\)\[\]\{\}¡!¿?\"\'/]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def load_and_clean_pdfs(subject):
    """Cargar y limpiar texto de PDFs usando pdfplumber"""
    data_dir = f"data/{subject}"
    documents = []
    
    # Procesar cada PDF en la carpeta
    for filename in os.listdir(data_dir):
        if filename.endswith(".pdf"):
            file_path = os.path.join(data_dir, filename)
            
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page_num, page in enumerate(pdf.pages):
                        raw_text = page.extract_text()
                        if raw_text:
                            cleaned_text = clean_text(raw_text)
                            if cleaned_text:  # Solo si hay texto después de limpiar
                                documents.append(
                                    Document(
                                        page_content=cleaned_text,
                                        metadata={
                                            "source": filename,
                                            "page": page_num
                                        }
                                    )
                                )
            except Exception as e:
                print(f"⚠️ Error procesando {filename}: {str(e)}")
    
    # Guardar texto limpio en archivo
    with open(os.path.join(data_dir, "clean_text.txt"), "w", encoding="utf-8") as f:
        for doc in documents:
            f.write(f"--- [Fuente: {doc.metadata['source']}, Página: {doc.metadata['page']}] ---\n")
            f.write(doc.page_content + "\n\n")
    
    return documents

def generate_training_data(subject):
    """Generar datos de entrenamiento a partir de PDFs limpios"""
    data_dir = f"data/{subject}"
    if not os.path.exists(data_dir):
        raise ValueError(f"La carpeta 'data/{subject}' no existe")

    # 1. Cargar y limpiar PDFs
    print("⏳ Cargando y limpiando PDFs...")
    documents = load_and_clean_pdfs(subject)

    # 2. Dividir texto en chunks
    print("✂️ Dividiendo texto en chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = text_splitter.split_documents(documents)

    # 3. Cargar modelos
    print("🤖 Cargando modelos de Hugging Face...")
    question_tokenizer = AutoTokenizer.from_pretrained(QUESTION_MODEL,
    token=HF_TOKEN,
    trust_remote_code=True,
    local_files_only=False,  # Forzar descarga remota
    force_download=True       # Ignorar caché existente
	)

    question_model = AutoModelForSeq2SeqLM.from_pretrained(QUESTION_MODEL).to(DEVICE)
    
    summarizer_tokenizer = AutoTokenizer.from_pretrained(SUMMARIZER_MODEL)
    summarizer_model = AutoModelForSeq2SeqLM.from_pretrained(SUMMARIZER_MODEL).to(DEVICE)

    # 4. Generar preguntas y respuestas
    print("🧠 Generando preguntas y respuestas...")
    train_data = []
    batch_size = 8

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        for chunk in batch:
            # Generar pregunta
            question_inputs = question_tokenizer(
                f"Genera una pregunta sobre: {chunk.page_content}",
                return_tensors="pt",
                max_length=512,
                truncation=True
            ).to(DEVICE)
            
            question = question_tokenizer.decode(
                question_model.generate(**question_inputs)[0],
                skip_special_tokens=True
            )
            
            # Generar respuesta (resumen)
            summary_inputs = summarizer_tokenizer(
                chunk.page_content,
                return_tensors="pt",
                max_length=512,
                truncation=True
            ).to(DEVICE)
            
            summary = summarizer_tokenizer.decode(
                summarizer_model.generate(**summary_inputs)[0],
                skip_special_tokens=True
            )
            
            train_data.append({
                "question": question,
                "answer": summary,
                "source": chunk.metadata["source"],
                "page": chunk.metadata["page"]
            })

    # Guardar datos en JSON
    output_file = os.path.join(data_dir, "train_data.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(train_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Datos generados: {output_file} ({len(train_data)} preguntas)")

if __name__ == "__main__":
    subject = input("Introduce la asignatura: ").strip().lower()
    generate_training_data(subject)
