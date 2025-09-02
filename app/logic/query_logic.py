import os
import re
from langchain_chroma import Chroma
from get_embedding_function import get_embedding_function
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.messages import HumanMessage, SystemMessage

from graph import build_graph, AgentState # Importa AgentState también

load_dotenv()

# =====================================
# ============ CONFIGURACIÓN ==========
# =====================================

VLLM_URL = os.getenv("VLLM_URL") + "/v1"
VLLM_MODEL_NAME = os.getenv("MODEL_DIR") 

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

# =====================================

#Poner como función para iniciar en la api_router
rag_graph = build_graph()

system_prompt = SystemMessage(
        content="""Eres un asistente experto. Tu trabajo es responder preguntas usando las herramientas proporcionadas.
Analiza la pregunta del usuario y usa **obligatoriamente** una de estas dos herramientas:
1. `consultar_guia_docente`: Para preguntas sobre la estructura del curso (profesores, temario, evaluación).
2. `chroma_retriever`: Para todas las demás preguntas conceptuales sobre el material de la asignatura.
Nunca respondas desde tu conocimiento previo. Siempre usa una herramienta. Una vez que la herramienta devuelva información, úsala para formular la respuesta final."""
    )

def query_rag(query_text: str,
              subject: str = None,
              use_finetuned: bool = False,
              ) -> dict:
    """
    Realiza búsqueda RAG y genera una respuesta.
    """

    model_desc = None

    if use_finetuned and subject: 
        model_desc = "RAG + LoRA"
    else:
        model_desc = "base"    

    conversation_id = "-".join(["email", subject]) 
    config = {
        "configurable": {
            "thread_id": conversation_id,
            "subject": subject,
            }
        }
    
    existing_state: AgentState = rag_graph.get_state(config)

    input_data = {}
    
    if not existing_state or not existing_state.values.get("messages"):
        print(f"--- INFO: Creando nueva conversación con ID: {conversation_id} ---")
        input_data = {
            "messages": [system_prompt, HumanMessage(content=query_text)],
            "subject": subject,
            "retrieved_docs": []
        }
    else:
        print(f"--- INFO: Continuando conversación con ID: {conversation_id} ---")
        input_data = {
            "messages": [HumanMessage(content=query_text)]
        }

    #ASYNC PARA STREAMING?
    final_result = None
    for event in rag_graph.stream(input_data, config=config, stream_mode="values"):
        # "values" nos da el estado completo después de cada paso
        final_result = event


    final_response_message = final_result["messages"][-1]
    final_response = final_response_message.content if final_response_message else "No se pudo generar respuesta."
    
    final_docs = final_result.get('retrieved_docs', [])
    sources = [doc.metadata.get("source", "N/A") for doc in final_docs]

    print(f"Fuentes recuperadas: {sources}")

    return {"response": final_response, "sources": sources, "model_used": model_desc}

# Ejemplo de uso conversacional
if __name__ == "__main__":
    # ID de conversación que persistirá entre llamadas
    chat_id = "mi_chat_con_el_agente_1"
    
    print("Iniciando chat con el agente. Escribe 'salir' para terminar.")
    
    # Primera pregunta
    print("\n--- PRIMER TURNO ---")
    response_1 = query_rag(
        query_text="¿qué es un algoritmo greedy?",
        subject="metaheuristicas",
        conversation_id=chat_id
    )
    print(f"Agente: {response_1['response']}")
    
    # Segunda pregunta (el agente debería recordar el contexto si el modelo lo permite)
    print("\n--- SEGUNDO TURNO ---")
    response_2 = query_rag(
        query_text="¿y podrías darme un ejemplo de uno de esos algoritmos?",
        subject="metaheuristicas", # El subject debe ser consistente
        conversation_id=chat_id   # Usamos el MISMO ID
    )
    print(f"Agente: {response_2['response']}")