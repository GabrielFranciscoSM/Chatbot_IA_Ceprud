import os
import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain_chroma import Chroma
from get_embedding_function import get_embedding_function
from peft import PeftModel

# =====================================
# ============ CONFIGURACIÓN ==========
# =====================================
MODEL_NAME = "deepseek-ai/deepseek-llm-7b-chat"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Cargar modelos UNA VEZ al iniciar la aplicación
BASE_MODEL, TOKENIZER = None, None
EMBEDDING_FUNCTION = None


def initialize_models():
    """
    Inicializa los modelos y funciones necesarias.
    Esto debe llamarse una sola vez al iniciar la aplicación.
    """
    global BASE_MODEL, TOKENIZER, EMBEDDING_FUNCTION
    if BASE_MODEL is None or TOKENIZER is None:
        print("🌟 Cargando modelo base desde /app/models...")
        repo_id = "deepseek-ai/deepseek-llm-7b-chat"  # Nombre del repositorio correcto
        cache_dir = "/app/models"  # Ruta donde se almacenan los archivos del modelo
        
        TOKENIZER = AutoTokenizer.from_pretrained(
            repo_id,
            cache_dir=cache_dir,
            local_files_only=True,
            trust_remote_code=True
        )
        BASE_MODEL = AutoModelForCausalLM.from_pretrained(
            repo_id,
            cache_dir=cache_dir,
            local_files_only=True,
            torch_dtype=torch.float16,
            trust_remote_code=True
        ).to(DEVICE)
    
    if EMBEDDING_FUNCTION is None:
        print("🌟 Cargando función de embeddings...")
        EMBEDDING_FUNCTION = get_embedding_function()


def load_finetuned_model(subject):
    """
    Aplica fine-tuning si existe un adaptador para la asignatura.
    Args:
        subject (str): Nombre de la asignatura.
    Returns:
        model: Modelo ajustado o base.
    """
    adapter_path = f"/app/models/{subject}-deepseek-qlora"
    if os.path.exists(adapter_path):
        print(f"🌟 Usando modelo fine-tuneado para {subject}")
        return PeftModel.from_pretrained(BASE_MODEL, adapter_path).merge_and_unload().eval()
    print(f"⚠️ Modelo fine-tuneado no encontrado para {subject}. Usando modelo base")
    return BASE_MODEL


def generate_response(prompt, max_new_tokens=2048):
    """
    Genera una respuesta a partir de un prompt.
    Args:
        prompt (str): Prompt para el modelo.
        max_new_tokens (int): Número máximo de tokens en la respuesta.
    Returns:
        str: Respuesta generada.
    """
    inputs = TOKENIZER(prompt, return_tensors="pt", truncation=True, max_length=4096).to(DEVICE)
    with torch.no_grad():
        outputs = BASE_MODEL.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.6,
            top_p=0.95,
            pad_token_id=TOKENIZER.eos_token_id,
            num_beams=5,
            early_stopping=True
        )
    
    # Decodificar respuesta
    response = TOKENIZER.decode(outputs[0], skip_special_tokens=True)
    
    # Extraer la respuesta después del delimitador
    match = re.search(r"### RESPUESTA:\s*(.*)", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return response.replace(prompt, "").strip()


def build_prompt_with_history(user_message, history=None, context_text=None):
    """
    Construye un prompt que incluye el historial de conversaciones recientes.
    Args:
        user_message (str): Mensaje actual del usuario.
        history (list, optional): Historial de conversaciones [(pregunta1, respuesta1), ...].
        context_text (str, optional): Contexto RAG si está disponible.
    Returns:
        str: Prompt completo con historial.
    """
    prompt = (
        "RESPONDE A LAS SIGUIENTES PREGUNTAS CON EL CONTEXTO PROPORCIONADO, "
        "ERES UN BOT DE LA UGR EXPERTO EN LA MATERIA:\n\n"
    )
    
    # Añadir contexto RAG si está disponible
    if context_text:
        prompt += f"{context_text}\n\n"
    
    # Añadir historial de conversaciones
    if history:
        prompt += "HISTORIAL DE CONVERSACIÓN RECIENTE:\n"
        for q, a in history:
            prompt += f"Usuario: {q}\nBot: {a}\n\n"
    
    # Añadir la pregunta actual
    prompt += f"LA PREGUNTA ACTUAL A RESPONDER ES:\n{user_message}\n\n### RESPUESTA:"
    
    return prompt


def query_rag(query_text, chroma_path, subject=None, use_finetuned=False, history=None):
    """
    Consultar el sistema RAG con respuesta limpia.
    Args:
        query_text (str): La pregunta del usuario.
        chroma_path (str): Ruta al directorio de Chroma.
        subject (str): Asignatura específica.
        use_finetuned (bool): Indica si se usa fine-tuning.
        history (list, optional): Historial de conversaciones [(pregunta1, respuesta1), ...].
    Returns:
        dict: Respuesta generada y fuentes.
    """
    # 1. Codificación UTF-8
    query_text = query_text.encode("utf-8", errors="ignore").decode("utf-8")

    # 2. Recuperar contexto relevante
    try:
        db = Chroma(persist_directory=chroma_path, embedding_function=EMBEDDING_FUNCTION)
        results = db.similarity_search_with_score(query_text, k=5)
    except Exception as e:
        return {"response": f"❌ Error en RAG: {str(e)}", "sources": []}

    if not results:
        return {"response": "No hay documentos relevantes", "sources": []}

    # 3. Construir prompt con delimitadores claros e historial
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt = build_prompt_with_history(query_text, history, context_text)

    # 4. Generar respuesta limpia
    response_text = generate_response(prompt)
    
    # 5. Extraer fuentes
    sources = [doc.metadata.get("id", "N/A") for doc, _score in results]
    
    return {
        "response": response_text,
        "sources": sources,
        "model_used": f"{'RAG+LoRA' if use_finetuned else 'RAG base'}"
    }


def get_base_model_response(query_text, history=None):
    """
    Generar respuesta directa del modelo base sin RAG.
    Args:
        query_text (str): La pregunta del usuario.
        history (list, optional): Historial de conversaciones [(pregunta1, respuesta1), ...].
    Returns:
        dict: Respuesta generada y fuentes vacías.
    """
    query_text = query_text.encode("utf-8", errors="ignore").decode("utf-8")
    
    # Prompt con historial para el modelo base
    prompt = build_prompt_with_history(query_text, history)
    response_text = generate_response(prompt)

    return {
        "response": response_text,
        "sources": [],
        "model_used": "base"
    }


# =====================================
# =========== INICIALIZACIÓN ==========
# =====================================
initialize_models()

# =====================================
# =========== EJEMPLO DE USO ==========
# =====================================
if __name__ == "__main__":
    # Ejemplo de historial de chat
    ejemplo_historial = [
        ("¿Cuál es el horario de las tutorías?", "Las tutorías son los lunes y miércoles de 10:00 a 12:00 en el despacho 3.14"),
        ("¿Qué temas se verán en el examen?", "El examen abarcará todos los temas vistos en clase hasta la fecha, con especial énfasis en algoritmos genéticos y búsqueda tabú.")
    ]
    
    # Prueba RAG base con historial
    print("=== RAG BASE CON HISTORIAL ===")
    respuesta_base = query_rag(
        "¿En qué aula se dan las clases de teoría?",
        chroma_path="/app/chroma/metaheuristicas",
        subject="metaheuristicas",
        use_finetuned=False,
        history=ejemplo_historial
    )
    print("Respuesta (base):", respuesta_base["response"])

    # Prueba RAG + LoRA con historial
    print("\n=== RAG + LoRA CON HISTORIAL ===")
    respuesta_lora = query_rag(
        "¿En qué aula se dan las clases de teoría?",
        chroma_path="/app/chroma/metaheuristicas",
        subject="metaheuristicas",
        use_finetuned=True,
        history=ejemplo_historial
    )
    print("Respuesta (LoRA):", respuesta_lora["response"])