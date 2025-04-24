import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain_chroma import Chroma
from get_embedding_function import get_embedding_function
from peft import PeftModel
import os
import re

# =====================================
# ============ CONFIGURACIÓN ==========
# =====================================
MODEL_NAME = "deepseek-ai/deepseek-llm-7b-chat"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def load_base_model():
    """Cargar el modelo base desde Hugging Face."""
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        trust_remote_code=True
    ).to(DEVICE)
    return tokenizer, model

def load_finetuned_model(base_model, subject):
    """Aplicar fine-tuning si existe un adaptador para la asignatura."""
    adapter_path = f"./models/{subject}-deepseek-qlora"
    if os.path.exists(adapter_path):
        print(f"🌟 Usando modelo fine-tuneado para {subject}")
        return PeftModel.from_pretrained(base_model, adapter_path).merge_and_unload().eval()
    print(f"⚠️ Modelo fine-tuneado no encontrado para {subject}. Usando modelo base")
    return base_model

def generate_response(model, tokenizer, query_text, max_new_tokens=2048):
    """
    Generar respuesta limpia del modelo sin incluir el prompt.
    
    Args:
        model: Modelo de lenguaje cargado.
        tokenizer: Tokenizer asociado al modelo.
        query_text (str): Texto de entrada (incluyendo contexto y pregunta).
        max_new_tokens (int): Máximo número de tokens a generar.
    
    Returns:
        str: Respuesta limpia del modelo.
    """
    inputs = tokenizer(query_text, return_tensors="pt", truncation=True, max_length=4096).to(DEVICE)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.6,
            top_p=0.95,
            pad_token_id=tokenizer.eos_token_id,
            num_beams=5,
            early_stopping=True
        )
    
    # Decodificar respuesta completa
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Eliminar el prompt de la respuesta
    if response.startswith(query_text):
        response = response[len(query_text):].strip()
    if response.endswith(query_text):
        response = response[:-len(query_text)].strip()

    # Si no encuentra el delimitador, eliminar el prompt manualmente
    response = response.replace(query_text, "").strip()
    
    return response.encode("utf-8", errors="ignore").decode("utf-8")

def query_rag(query_text, chroma_path, subject=None, use_finetuned=False):
    """
    Consultar el sistema RAG con respuesta limpia.
    
    Args:
        query_text (str): La pregunta del usuario.
        chroma_path (str): Ruta al directorio de Chroma.
        subject (str): Asignatura específica.
        use_finetuned (bool): Indica si se usa fine-tuning.
    
    Returns:
        dict: Respuesta generada y fuentes.
    """
    # 1. Codificación UTF-8
    query_text = query_text.encode("utf-8", errors="ignore").decode("utf-8")

    # 2. Cargar modelo base
    tokenizer, base_model = load_base_model()

    # 3. Aplicar fine-tuning si se especifica
    if use_finetuned and subject:
        base_model = load_finetuned_model(base_model, subject)

    # 4. Recuperar contexto relevante
    try:
        db = Chroma(persist_directory=chroma_path, embedding_function=get_embedding_function())
        results = db.similarity_search_with_score(query_text, k=5)
    except Exception as e:
        return {"response": f"❌ Error en RAG: {str(e)}", "sources": []}

    if not results:
        return {"response": "No hay documentos relevantes", "sources": []}

    # 5. Construir prompt con delimitadores claros
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt = f"""
    RESPONDE A LAS SIGUIENTES PREGUNTAS CON EL CONTEXTO PROPORCIONADO, ERES UN  BOT DE LA UGR EXPERTO EN LA MATERIA:
    {context_text}
    LA PREGUNTA A RESPONDER ES:
    {query_text}
    """

    # 6. Generar respuesta limpia
    response_text = generate_response(base_model, tokenizer, prompt)
    
    # 7. Extraer fuentes
    sources = [doc.metadata.get("id", "N/A") for doc, _score in results]
    
    return {
        "response": response_text,
        "sources": sources,
        "model_used": f"{'RAG+LoRA' if use_finetuned else 'RAG base'}"
    }

def get_base_model_response(query_text):
    """Generar respuesta directa del modelo base sin RAG."""
    tokenizer, model = load_base_model()
    query_text = query_text.encode("utf-8", errors="ignore").decode("utf-8")
    
    # Prompt simple para el modelo base
    prompt = f"""
    ERES UN  BOT DE LA UGR EXPERTO EN LA MATERIA, LA PREGUNTA A RESPONDER ES:
    {query_text}
    """
    return generate_response(model, tokenizer, prompt)

# =====================================
# =========== EJEMPLO DE USO ==========
# =====================================
if __name__ == "__main__":
    # Prueba RAG base
    print("=== RAG BASE ===")
    respuesta_base = query_rag(
        "¿En qué aula se dan las clases de teoría?",
        chroma_path="./chroma/metaheuristicas",
        subject="metaheuristicas",
        use_finetuned=False
    )
    print("Respuesta (base):", respuesta_base["response"])

    # Prueba RAG + LoRA
    print("\n=== RAG + LoRA ===")
    respuesta_lora = query_rag(
        "¿En qué aula se dan las clases de teoría?",
        chroma_path="./chroma/metaheuristicas",
        subject="metaheuristicas",
        use_finetuned=True
    )

    print("Respuesta (LoRA):", respuesta_lora["response"])
