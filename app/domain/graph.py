import json
import os
import sqlite3
from dotenv import load_dotenv
from typing import Literal, List, Dict, Any, Tuple
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from typing_extensions import TypedDict

from services.rag_client import rag_client
from langchain_core.runnables import RunnableConfig

# --- CONFIGURACIÓN ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
VLLM_URL = os.getenv("VLLM_URL", "http://localhost:8000") + "/v1"
VLLM_MODEL_NAME = os.getenv("MODEL_DIR", "/models/Sreenington--Phi-3-mini-4k-instruct-AWQ")

LOCAL_INFERENCE=False

# Estado del agente, incluyendo los documentos recuperados y la asignatura
class AgentState(MessagesState):
    retrieved_docs: List[Document]
    subject: str 

# --- HERRAMIENTAS ---

@tool
def consultar_guia_docente(seccion: str, config: RunnableConfig) -> Tuple[str, List[Document]]:
    """
    Consulta información específica de la guía docente de la asignatura.
    
    Secciones disponibles:
    - "profesorado" o "profesores": Información sobre profesores y tutorías
    - "evaluacion": Criterios y métodos de evaluación (ordinaria, extraordinaria, única final)
    - "temario" o "programa": Contenidos teóricos y prácticos organizados por temas
    - "metodologia": Metodologías docentes empleadas
    - "bibliografia": Referencias bibliográficas fundamentales y complementarias
    - "prerrequisitos": Prerrequisitos y recomendaciones previas
    - "competencias" o "resultados": Competencias y resultados de aprendizaje esperados
    - "enlaces": Enlaces recomendados y recursos web
    - "informacion_adicional": Información sobre NEAE y otros aspectos
    
    Usa esta herramienta para consultas sobre:
    - Quién imparte la asignatura y horarios de tutoría
    - Cómo se evalúa la asignatura y qué porcentajes tiene cada parte
    - Qué temas se ven en teoría y práctica
    - Qué metodologías se usan en clase
    - Qué libros se recomiendan
    - Qué conocimientos previos se necesitan
    """
    try:
        subject = config["configurable"]["subject"]

        # Usar el RAG client para obtener la guía docente
        guia_data = rag_client.get_guia_docente(subject, seccion)
        
        if not guia_data:
            error_msg = f"No se encontró información de guía docente para '{subject}'"
            return error_msg, []
        
        # La guía_data ya viene filtrada por sección desde el RAG service
        # Convertir a formato legible
        if isinstance(guia_data, dict):
            if len(guia_data) == 1:
                # Solo una sección
                key, value = next(iter(guia_data.items()))
                content = f"=== {key.replace('_', ' ').title()} ===\n\n"
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        content += f"**{subkey}**: {subvalue}\n\n"
                else:
                    content += str(value)
            else:
                # Múltiples secciones
                content = ""
                for key, value in guia_data.items():
                    content += f"=== {key.replace('_', ' ').title()} ===\n\n"
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            content += f"**{subkey}**: {subvalue}\n\n"
                    else:
                        content += str(value) + "\n\n"
        else:
            content = str(guia_data)
        
        # Crear documento con la información
        doc = Document(
            page_content=content,
            metadata={
                "source": f"guia_docente_{subject}",
                "section": seccion,
                "type": "guia_docente"
            }
        )
        
        return content, [doc]
        
    except Exception as e:
        error_msg = f"Error al consultar guía docente: {str(e)}"
        print(error_msg)
        return error_msg, []


@tool
def chroma_retriever(pregunta: str, config: RunnableConfig) -> Tuple[str, List[Document]]:
    """
    Busca en los apuntes de la asignatura usando el RAG Service.
    Esta herramienta es para preguntas conceptuales, sobre el material de estudio, etc.
    El 'subject' se inyectará desde la configuración del agente, no lo provee el LLM.
    """
    try:
        subject = config["configurable"]["subject"]
        
        # Usar el cliente RAG Service
        documents, sources = rag_client.search_documents(
            query=pregunta,
            subject=subject,
            k=6
        )
        
        if not documents:
            error_msg = f"No se encontraron documentos para la asignatura '{subject}' en el RAG Service"
            return error_msg, []
        
        # Formatear resultados
        formatted_results = []
        formatted_results.append(f"Encontrados {len(documents)} documentos relevantes:\n")
        
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "Fuente desconocida")
            page = doc.metadata.get("page", "N/A")
            
            formatted_results.append(f"--- Resultado {i} ---")
            formatted_results.append(f"Fuente: {source}")
            if page != "N/A":
                formatted_results.append(f"Página: {page}")
            formatted_results.append(f"Contenido: {doc.page_content}")
            formatted_results.append("")
        
        return "\n".join(formatted_results), documents
        
    except KeyError as e:
        error_msg = f"Error: Falta configuración requerida: {str(e)}"
        return error_msg, []
    except Exception as e:
        error_msg = f"Error en búsqueda RAG: {str(e)}"
        return error_msg, []

# --- LÓGICA DEL GRAFO ---

def call_agent(state: AgentState):
    """Nodo del Agente. Decide si responder o usar una herramienta."""

    if LOCAL_INFERENCE:
        llm = ChatOpenAI(model=VLLM_MODEL_NAME, openai_api_key="EMPTY", openai_api_base=VLLM_URL, temperature=0)
    else:
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",temperature=0)

    tools = [consultar_guia_docente, chroma_retriever]
    
    llm_with_tools = llm.bind_tools(tools)

    response = llm_with_tools.invoke(state["messages"])

    return {"messages": [response]}


def execute_tools(state: AgentState) -> Dict[str, Any]:
    """
    Ejecuta las herramientas. Extrae dependencias (como 'subject') del estado
    y las inyecta en la llamada a la herramienta. Maneja correctamente la salida.
    """
    last_message = state['messages'][-1]
    tool_calls = last_message.tool_calls
    
    # Este mapa es crucial para llamar a la función correcta.
    tool_map = {"consultar_guia_docente": consultar_guia_docente, "chroma_retriever": chroma_retriever}
    
    tool_messages = []
    all_retrieved_docs = []
    
    for call in tool_calls:
        tool_name = call['name']
        
        tool_function = tool_map.get(tool_name)
        if not tool_function:
            error_message = f"Error: La herramienta '{tool_name}' no existe."
            tool_messages.append(ToolMessage(content=error_message, tool_call_id=call['id']))
            continue

        tool_args = call['args']

        # Create proper config with subject from state
        config = RunnableConfig(
            configurable={
                "subject": state.get("subject", "unknown"),
                "thread_id": "default"
            }
        )

        try:
            content, docs = tool_function.invoke(tool_args, config)
            tool_messages.append(ToolMessage(content=content, tool_call_id=call['id']))
            if docs:
                all_retrieved_docs.extend(docs)
        except Exception as e:
            error_msg = f"Error al ejecutar la herramienta {tool_name}: {e}"
            tool_messages.append(ToolMessage(content=error_msg, tool_call_id=call['id']))

    return {"messages": tool_messages, "retrieved_docs": all_retrieved_docs}

def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    """Router: Decide si el ciclo continúa o termina."""
    if not state['messages'] or not isinstance(state['messages'][-1], AIMessage):
        return "agent" 
    
    return "tools" if state["messages"][-1].tool_calls else "__end__"

# --- CONSTRUCCIÓN DEL GRAFO ---

def build_graph():
    """Construye y compila el grafo del agente."""
    graph_builder = StateGraph(AgentState)
    
    graph_builder.add_node("agent", call_agent)
    graph_builder.add_node("tools", execute_tools)

    graph_builder.set_entry_point("agent")
    graph_builder.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", "__end__": "__end__"}
    )
    graph_builder.add_edge("tools", "agent")

    # Use storage directory for checkpoints - persistent across container restarts
    # Create storage directory if it doesn't exist
    storage_dir = os.path.join(os.path.dirname(__file__), "..", "storage")
    os.makedirs(storage_dir, exist_ok=True)
    
    checkpoint_path = os.path.join(storage_dir, "checkpoints.sqlite")
    conn = sqlite3.connect(checkpoint_path, check_same_thread=False)
    memory = SqliteSaver(conn)

    return graph_builder.compile(checkpointer=memory)

# --- EJECUCIÓN ---

if __name__ == '__main__':
    graph = build_graph()
    thread_config = {"configurable": {"thread_id": "test_run_1"}}

    # Un prompt de sistema más directo puede ayudar al modelo
    system_prompt = SystemMessage(
        content="""Eres un asistente experto especializado en responder preguntas sobre asignaturas universitarias. 
Tu trabajo es responder preguntas usando las herramientas proporcionadas de manera precisa y útil.

HERRAMIENTAS DISPONIBLES:

1. **consultar_guia_docente**: Usa esta herramienta para consultas sobre:
   - Información del profesorado y horarios de tutoría
   - Criterios y métodos de evaluación (exámenes, porcentajes, etc.)
   - Temario y programa de contenidos (qué temas se ven)
   - Metodología docente empleada
   - Bibliografía recomendada
   - Prerrequisitos y conocimientos previos necesarios
   - Competencias y resultados de aprendizaje
   - Enlaces y recursos adicionales

2. **chroma_retriever**: Usa esta herramienta para consultas sobre:
   - Conceptos específicos de la materia (definiciones, explicaciones)
   - Contenido detallado de los temas
   - Ejemplos y aplicaciones prácticas
   - Algoritmos, fórmulas o procedimientos específicos

INSTRUCCIONES:
- Analiza cuidadosamente la pregunta del usuario para determinar qué herramienta es más apropiada
- Para la guía docente, especifica claramente la sección que necesitas (ej: "evaluacion", "profesores", "temario")
- Una vez que obtengas información de las herramientas, úsala para formular una respuesta completa y útil
- Si la información no es suficiente, puedes usar ambas herramientas de forma complementaria

Ejemplo de uso:
- "¿Quién es el profesor?" → usar consultar_guia_docente con sección "profesores"
- "¿Cómo se evalúa la asignatura?" → usar consultar_guia_docente con sección "evaluacion"  
- "¿Qué es una metaheurística?" → usar chroma_retriever
- "¿Qué temas se ven en la asignatura?" → usar consultar_guia_docente con sección "temario"
"""
    )
    
    # PREGUNTA DE PRUEBA para probar la guía docente
    pregunta_usuario = "¿Quién es el profesor de la asignatura y cómo se evalúa?"
    asignatura = "metaheuristicas" 

    initial_state = {
        "messages": [system_prompt, HumanMessage(content=pregunta_usuario)],
        "subject": asignatura,
        "retrieved_docs": []
    }
    
    final_agent_response = None
    # Usamos .stream() para ver cada paso del proceso
    events = graph.stream(initial_state, config=thread_config)
    for event in events:
        # Busca el evento final del nodo 'agent' que no tiene tool_calls
        if "agent" in event:
            last_msg = event["agent"].get("messages", [])[-1]
            if isinstance(last_msg, AIMessage) and not last_msg.tool_calls:
                 final_agent_response = last_msg

    # Mostrar la respuesta y los documentos recuperados del estado final
    if final_agent_response:
        # In production, we just return the response without printing
        pass

    # Recupera el estado final completo para verificar los documentos
    final_state = graph.get_state(thread_config)
    final_docs = final_state.values.get('retrieved_docs')
    if final_docs:
        # In production, we just use the docs without printing
        pass