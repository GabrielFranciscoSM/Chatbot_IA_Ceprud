import os
import re
from langchain_chroma import Chroma
from get_embedding_function import get_embedding_function
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage,HumanMessage,AIMessage

from graph import buildGraph

load_dotenv()

# =====================================
# ============ CONFIGURACIÓN ==========
# =====================================
# Ruta al modelo base
VLLM_URL = os.getenv("VLLM_URL") + "/v1"#.join("/v1/chat/completions")
VLLM_MODEL_NAME = os.getenv("MODEL_DIR")  # O el nombre servido
rag_graph = buildGraph()



def query_rag(query_text: str,
              chroma_path: str,
              subject: str = None,
              use_finetuned: bool = False,
              history: list[tuple[str, str]] = None) -> dict:
    """
    Realiza búsqueda RAG y genera una respuesta.
    """

    model = None
    model_desc = None

    if use_finetuned and subject:
        model = ChatOpenAI(base_url=VLLM_URL,model=subject,api_key="LOCAL")
 
        model_desc = "RAG + LoRA"
    else:
        model = ChatOpenAI(base_url=VLLM_URL,model=VLLM_MODEL_NAME,api_key="LOCAL") 
        model_desc = "base"

    # Normalizar texto UTF-8
    conversation_id = "user-123-session-abc"
    config = {"configurable": {"thread_id": conversation_id}}

    result = rag_graph.invoke(config=config,input={"messages": [HumanMessage(content=query_text)], "vector_store": chroma_path, "llm": model})
    final_response = result['messages'][-1].content
    source = [d.metadata.get("id", "N/A") for d in result['context']]

    return {"response": final_response, "sources": source, "model_used": model_desc}


def generate_response(
    prompt: str,
    max_new_tokens: int = 1000, #Hay que revisar esto y echarle un ojo
    model_name: str = VLLM_MODEL_NAME,
) -> str:
    """
    Genera una respuesta.
    """

    llm = ChatOpenAI(base_url=VLLM_URL,model=VLLM_MODEL_NAME,api_key="LOCAL")

    try:
        
        data = llm.invoke(prompt)

        text = data.content

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
