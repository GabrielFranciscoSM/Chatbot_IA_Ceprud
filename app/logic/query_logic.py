import os
import re
from langchain_chroma import Chroma
from get_embedding_function import get_embedding_function
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.messages import HumanMessage, SystemMessage

from graph import buildGraph

load_dotenv()

# =====================================
# ============ CONFIGURACIÓN ==========
# =====================================

VLLM_URL = os.getenv("VLLM_URL") + "/v1"
VLLM_MODEL_NAME = os.getenv("MODEL_DIR") 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

# =====================================

rag_graph = buildGraph()


def query_rag(query_text: str,
              chroma_path: str = "",
              subject: str = None,
              use_finetuned: bool = False,
              use_RAG: bool = True,
              ) -> dict:
    """
    Realiza búsqueda RAG y genera una respuesta.
    """
    model_desc = None

    if use_finetuned and subject: 
        model_desc = "RAG + LoRA"
    else:
        model_desc = "base"

    conversation_id =  "-".join(["email",subject]) 
    config = {"configurable": {"thread_id": conversation_id}}

    result = rag_graph.invoke(
        config=config,
        input={
            "messages": [HumanMessage(content=query_text)], 
            "chorma_path": chroma_path, 
            "use_RAG": use_RAG
            }
        )
    
    final_response = result['messages'][-1].content
    source = [d.metadata.get("id", "N/A") for d in result['context']]

    for message in result["messages"]:
        message.pretty_print()

    return {"response": final_response, "sources": source, "model_used": model_desc}


# def build_prompt_with_history(user_message: str,
#                               history: list[tuple[str, str]] = None,
#                               context_text: str = None) -> str:
#     """
#     Construye el prompt que incluye contexto y/o historial.
#     """
#     parts = [
#         "RESPONDE A LAS SIGUIENTES PREGUNTAS CON EL CONTEXTO PROPORCIONADO, ERES UN BOT DE LA UGR EXPERTO EN LA MATERIA:\n"
#     ]
#     if context_text:
#         parts.append(context_text + "\n\n")
#     if history:
#         parts.append("HISTORIAL DE CONVERSACIÓN RECIENTE:\n")
#         for q, a in history:
#             parts.append(f"Usuario: {q}\nBot: {a}\n\n")
#     parts.append(f"LA PREGUNTA ACTUAL A RESPONDER ES:\n{user_message}\n\n### RESPUESTA:")
#     return "".join(parts)


# Ejemplo de uso
if __name__ == "__main__":
    hist = [
        ("¿Cuál es el horario de las tutorías?", "Lunes y miércoles de 10:00 a 12:00."),
        ("¿Qué temas en el examen?", "Algoritmos genéticos y búsqueda tabú.")
    ]
    print(query_rag("¿Dónde se dan las clases de teoría?", "/app/chroma/metaheuristicas", "metaheuristicas", use_finetuned=False, history=hist))
