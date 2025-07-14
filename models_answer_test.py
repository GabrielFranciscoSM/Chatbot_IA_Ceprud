import csv
import os
from query_logic import query_rag, get_base_model_response  # Importar nueva función

# Configuración
ANSWERS_DIR = "answers"
os.makedirs(ANSWERS_DIR, exist_ok=True)

def test_all_models(subject, question):
    # Verificar si existe la base de datos Chroma para la asignatura
    chroma_path = f"./chroma/{subject}"
    if not os.path.exists(chroma_path):
        print(f"⚠️ Chroma no encontrado para {subject}. Saltando...")
        return

    # Respuesta modelo base (sin RAG ni fine-tuning)
    base_resp = get_base_model_response(question)
    
    # Respuesta RAG base
    rag_base_resp = query_rag(
        question,
        chroma_path=chroma_path,
        subject=subject,
        use_finetuned=False
    )

    # Respuesta RAG + LoRA
    rag_lora_resp = query_rag(
        question,
        chroma_path=chroma_path,
        subject=subject,
        use_finetuned=True
    )

    # Guardar en CSV
    file_path = os.path.join(ANSWERS_DIR, "answers.csv")
    try:
        with open(file_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "asignatura", "pregunta",
                "respuesta_base", "respuesta_rag_base", "respuesta_rag_lora",
                "fuentes_rag_base", "fuentes_rag_lora"
            ])
            
            if f.tell() == 0:
                writer.writeheader()
            
            writer.writerow({
                "asignatura": subject,
                "pregunta": question,
                "respuesta_base": base_resp,
                "respuesta_rag_base": rag_base_resp["response"],
                "respuesta_rag_lora": rag_lora_resp["response"],
                "fuentes_rag_base": ";".join(rag_base_resp["sources"]),
                "fuentes_rag_lora": ";".join(rag_lora_resp["sources"])
            })
        print(f"✅ Respuestas guardadas para {subject}: {question}")
    except Exception as e:
        print(f"❌ Error guardando respuestas: {str(e)}")

if __name__ == "__main__":
    preguntas = [
        "¿Qué es una metaheurística?",
        "¿Cómo funciona el algoritmo genético?",
        "¿Qué problemas resuelve la optimización por colonias de hormigas?"
    ]

    # Obtener asignaturas desde ./data
    for subject in os.listdir("./data"):
        if os.path.isdir(f"./data/{subject}"):
            print(f"\n🔍 Probando asignatura: {subject}")
            for pregunta in preguntas:
                test_all_models(subject, pregunta)