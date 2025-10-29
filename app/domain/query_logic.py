import os
import re
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.messages import HumanMessage, SystemMessage

from domain.graph import build_graph, AgentState # Importa AgentState también
from langchain_core.prompts import PromptTemplate

# Langfuse imports for tracing
from langfuse import Langfuse, get_client
from langfuse.langchain import CallbackHandler

load_dotenv()

# =====================================
# ============ CONFIGURACIÓN ==========
# =====================================

VLLM_URL = os.getenv("VLLM_URL") + "/v1"
VLLM_MODEL_NAME = os.getenv("MODEL_DIR", "/models/Sreenington--Phi-3-mini-4k-instruct-AWQ") 

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

# =====================================
# ========= LANGFUSE SETUP ============
# =====================================

# Initialize Langfuse client (uses environment variables)
Langfuse()
langfuse = get_client()

# Safe flush helper (module-level) — prevents the app from crashing if Langfuse collector is unreachable
def safe_flush(client):
    try:
        client.flush()
    except Exception as e:
        # Catch connection errors to the Langfuse collector (e.g., connection refused)
        # Do not re-raise; just log and continue.
        try:
            import logging
            logging.getLogger(__name__).warning(f"Langfuse flush failed: {e}")
        except Exception:
            pass

# =====================================

#Poner como función para iniciar en la api_router
rag_graph = build_graph()

System_prompt_template = PromptTemplate.from_template("""Eres un asistente académico especializado en {subject}. Tu función es responder preguntas usando SIEMPRE las herramientas disponibles.

## REGLAS OBLIGATORIAS:

1. **NUNCA pidas permiso para usar herramientas** - Úsalas directamente y automáticamente
2. **NUNCA preguntes qué información quiere el usuario** - Busca toda la información relevante inmediatamente
3. **USA las herramientas EN CADA RESPUESTA** antes de contestar

## HERRAMIENTAS (úsalas automáticamente):

### chroma_retriever
**USA PRIMERO** para TODAS las preguntas sobre conceptos, definiciones, teoría o contenido académico.
Busca automáticamente información en los apuntes y documentos de la asignatura.

### consultar_guia_docente  
**USA** para preguntas sobre: profesorado, evaluación, temario, metodología, bibliografía, prerrequisitos, competencias, recursos.

## PROTOCOLO OBLIGATORIO:

**PASO 1:** Lee la pregunta del usuario
**PASO 2:** USA inmediatamente la herramienta correspondiente (chroma_retriever para contenido académico, consultar_guia_docente para info administrativa)
**PASO 3:** Con los resultados obtenidos, redacta una respuesta clara y completa

## FORMATO DE RESPUESTA:

1. **Respuesta directa** basada en la información recuperada
2. **Explicación detallada** con ejemplos si es necesario
3. **Contexto adicional** relacionando con otros temas de la asignatura
4. **Síntesis** de los puntos clave

## EJEMPLOS DE USO CORRECTO:

Usuario: "¿Qué es la estimación puntual?"
✅ CORRECTO: Usar chroma_retriever inmediatamente → Responder con la información encontrada

❌ INCORRECTO: "¿Quieres que busque en los documentos?" o "¿Qué información específica necesitas?"

Usuario: "¿Cómo se evalúa la asignatura?"  
✅ CORRECTO: Usar consultar_guia_docente con sección "evaluacion" → Responder con los criterios

❌ INCORRECTO: Pedir más detalles sobre qué aspecto de la evaluación

## TONO:
Claro, directo, académico pero accesible. Responde con confianza basándote en la información recuperada.
""")




def query_rag(query_text: str,
              subject: str = None,
              use_finetuned: bool = False,
              email: str = "anonymous"
              ) -> dict:
    """
    Realiza búsqueda RAG y genera una respuesta.
    """

    system_prompt = SystemMessage(
        content=System_prompt_template.invoke({"subject": subject}).text
        )
    
    model_desc = None

    if use_finetuned and subject: 
        model_desc = "RAG + LoRA"
    else:
        model_desc = "base"    

    conversation_id = "-".join([email, subject]) 
    config = {
        "configurable": {
            "thread_id": conversation_id,
            "subject": subject,
            "email": email,
        },
        "callbacks": [CallbackHandler()],
        "metadata": {
            "langfuse_user_id": email,
            "langfuse_session_id": conversation_id,
            "langfuse_tags": [subject, model_desc, "query"],
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

    # Flush Langfuse events to ensure they are sent (safe - don't crash on connection errors)
    safe_flush(langfuse)

    return {"response": final_response, "sources": sources, "model_used": model_desc}

def clear_session(subject: str, email: str) -> bool:
    """
    Limpia la memoria de una sesión específica (email + subject).
    
    Args:
        subject: Nombre de la asignatura
        email: Email del usuario
        
    Returns:
        bool: True si la sesión fue limpiada exitosamente
    """
    import time
    try:
        conversation_id = "-".join([email, subject])
        config = {
            "configurable": {
                "thread_id": conversation_id,
                "subject": subject,
                "email": email,
            }
        }
        
        # Verificar si existe estado previo
        existing_state = rag_graph.get_state(config)
        
        if existing_state and existing_state.values.get("messages"):
            print(f"--- INFO: Limpiando sesión con ID: {conversation_id} ---")
            
            # Create system prompt for clean state
            clean_system_prompt = SystemMessage(
                content=System_prompt_template.invoke({"subject": subject}).text
            )
            
            # Crear estado inicial limpio (solo con system prompt)
            clean_state = {
                "messages": [clean_system_prompt],  # Solo system prompt, sin historia
                "subject": subject,
                "retrieved_docs": []
            }
            
            # Sobrescribir completamente el estado
            try:
                rag_graph.update_state(config, clean_state, as_node="__start__")
                print(f"--- INFO: Estado completamente reiniciado ---")
            except Exception as update_error:
                print(f"--- WARNING: Error con as_node: {update_error} ---")
                # Fallback sin as_node
                rag_graph.update_state(config, clean_state)
                print(f"--- INFO: Estado reiniciado (fallback) ---")
                
            print(f"--- INFO: Sesión {conversation_id} limpiada exitosamente ---")
            
            # Flush Langfuse events (safe)
            safe_flush(langfuse)
            
            return True
        else:
            print(f"--- INFO: No hay sesión existente para limpiar: {conversation_id} ---")
            return True  # Consideramos exitoso si no hay nada que limpiar
            
    except Exception as e:
        print(f"--- ERROR: Error al limpiar sesión {email}-{subject}: {str(e)} ---")
        return False

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
        email="test@correo.ugr.es"
    )
    print(f"Agente: {response_1['response']}")
    
    # Segunda pregunta (el agente debería recordar el contexto si el modelo lo permite)
    print("\n--- SEGUNDO TURNO ---")
    response_2 = query_rag(
        query_text="¿y podrías darme un ejemplo de uno de esos algoritmos?",
        subject="metaheuristicas", # El subject debe ser consistente
        email="test@correo.ugr.es"   # El email debe ser consistente
    )
    print(f"Agente: {response_2['response']}")