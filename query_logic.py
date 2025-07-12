import os
import re
from langchain_chroma import Chroma
from get_embedding_function import get_embedding_function
import requests

# =====================================
# ============ CONFIGURACIÓN ==========
# =====================================
# Ruta al modelo base
VLLM_URL = "http://vllm-openai:8000/v1/chat/completions" 
VLLM_MODEL_NAME = "/models/TinyLlama--TinyLlama-1.1B-Chat-v1.0"  # O el nombre servido

EMBEDDING_FUNCTION = None

# def load_finetuned_model(subject: str) -> AutoModelForCausalLM:
#     """
#     Carga y aplica un adaptador LoRA si existe, o retorna el modelo base.
#     """
#     adapter_dir = os.path.join(os.path.dirname(__file__), "models", f"{subject}-deepseek-qlora")
#     if os.path.isdir(adapter_dir):
#         print(f"🌟 Usando modelo fine-tuneado para '{subject}'")
#         model = PeftModel.from_pretrained(BASE_MODEL, adapter_dir)
#         return model.merge_and_unload().eval()
#     print(f"⚠️ No se encontró adaptador para '{subject}', usando modelo base")
#     return BASE_MODEL


def generate_response(
    prompt: str,
    max_new_tokens: int = 1000 #Hay que revisar esto y echarle un ojo
) -> str:
    """
    Genera una respuesta usando el modelo y tokenizer indicados (o los globales).
    """
    
    payload = {
        "model": VLLM_MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_new_tokens,
        "temperature": 0.7
    }

    try:
        response = requests.post(VLLM_URL, json=payload)
        response.raise_for_status()

        data = response.json()
        text = data["choices"][0]["message"]["content"]
    


        match = re.search(r"### RESPUESTA:\s*(.*)", text, re.DOTALL)


        if match:
            return match.group(1).strip()

        return text.replace(prompt, "").strip()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al generar respuesta: {str(e)}")
        return


def build_prompt_with_history(user_message: str,
                              history: list[tuple[str, str]] = None,
                              context_text: str = None) -> str:
    """
    Construye el prompt que incluye contexto y/o historial.
    """
    parts = [
        "RESPONDE A LAS SIGUIENTES PREGUNTAS CON EL CONTEXTO PROPORCIONADO, ERES UN BOT DE LA UGR EXPERTO EN LA MATERIA:\n"
    ]
    if context_text:
        parts.append(context_text + "\n\n")
    if history:
        parts.append("HISTORIAL DE CONVERSACIÓN RECIENTE:\n")
        for q, a in history:
            parts.append(f"Usuario: {q}\nBot: {a}\n\n")
    parts.append(f"LA PREGUNTA ACTUAL A RESPONDER ES:\n{user_message}\n\n### RESPUESTA:")
    return "".join(parts)


def query_rag(query_text: str,
              chroma_path: str,
              subject: str = None,
              use_finetuned: bool = False,
              history: list[tuple[str, str]] = None) -> dict:
    """
    Realiza búsqueda RAG y genera una respuesta.
    """
    # Normalizar texto UTF-8
    query_text = query_text.encode("utf-8", errors="ignore").decode("utf-8")

    try:
        db = Chroma(persist_directory=chroma_path, embedding_function=get_embedding_function())
        docs_and_scores = db.similarity_search_with_score(query_text, k=5)
    except Exception as e:
        return {"response": f"❌ Error al acceder a ChromaDB: {str(e)}", "sources": []}

    if not docs_and_scores:
        return {"response": "No hay documentos relevantes.", "sources": []}

    docs, _ = zip(*docs_and_scores)
    context = "\n\n---\n\n".join(d.page_content for d in docs)
    prompt = build_prompt_with_history(query_text, history, context)

    # Seleccionar modelo
    # model_desc = "RAG base"
    # if use_finetuned and subject:
    #     model = load_finetuned_model(subject)
    #     model_desc = "RAG + LoRA"
    # else:
    #     model = BASE_MODEL

    # response = generate_response(prompt, model=model, tokenizer=TOKENIZER)
    sources = [d.metadata.get("id", "N/A") for d in docs]

    # return {"response": response, "sources": sources, "model_used": model_desc}
    return {"response": generate_response(prompt), "sources": sources, "model_used": "RAG"}


def get_base_model_response(query_text: str,
                            history: list[tuple[str, str]] = None) -> dict:
    """
    Genera respuesta directa sin RAG.
    """
    normalized = query_text.encode("utf-8", errors="ignore").decode("utf-8")
    prompt = build_prompt_with_history(normalized, history)
    resp = generate_response(prompt)
    return {"response": resp, "sources": [], "model_used": "base"}

# Ejemplo de uso
if __name__ == "__main__":
    hist = [
        ("¿Cuál es el horario de las tutorías?", "Lunes y miércoles de 10:00 a 12:00."),
        ("¿Qué temas en el examen?", "Algoritmos genéticos y búsqueda tabú.")
    ]
    print(query_rag("¿Dónde se dan las clases de teoría?", "/app/chroma/metaheuristicas", "metaheuristicas", use_finetuned=False, history=hist))
