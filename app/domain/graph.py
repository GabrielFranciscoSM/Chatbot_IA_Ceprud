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
from langchain_chroma import Chroma
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from typing_extensions import TypedDict

# Asumo que get_embedding_function es una función que tienes en otro archivo
from rag.get_embedding_function import get_embedding_function
from langchain_core.runnables import RunnableConfig
import sqlite3

# --- CONFIGURACIÓN ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
VLLM_URL = os.getenv("VLLM_URL", "http://localhost:8000") + "/v1"
VLLM_MODEL_NAME = ".." + os.getenv("MODEL_DIR", "default_model_name")
BASE_CHROMA_PATH = "../RAG" + os.getenv("BASE_CHROMA_PATH", "chroma")

LOCAL_INFERENCE=False

# Estado del agente, incluyendo los documentos recuperados y la asignatura
class AgentState(MessagesState):
    retrieved_docs: List[Document]
    subject: str # El campo para saber qué base de datos Chroma usar

# --- HERRAMIENTAS ---

@tool
def consultar_guia_docente(config: RunnableConfig, seccion: str) -> Tuple[str, List[Document]]:
    """
    Consulta la guía docente. Devuelve el texto y una lista vacía de documentos.
    Esta herramienta es para preguntas sobre la estructura del curso, profesores, evaluación, etc.
    """
    print(f"--- INFO: Usando herramienta 'Guía Docente' para la sección: {seccion} ---")

    subject = config["configurable"]["subject"]

    try:
        # Asume que la guía está en la raíz. Ajusta si es necesario.
        # Cambiar la guia docente predeterminada por la de la asignatura pertinente.
        with open('guia_docente_de_modelos_avanzados.json', 'r', encoding='utf-8') as f:
            guia = json.load(f)
    except FileNotFoundError:
        return "Error: El archivo de la guía docente no fue encontrado.", []
    seccion_limpia = seccion.lower().strip().replace(' ', '_')
    for key in guia.keys():
        if seccion_limpia in key.lower():
            return json.dumps({key: guia[key]}, ensure_ascii=False, indent=2), []
    return f"Error: La sección '{seccion}' no se encontró en la guía docente.", []


@tool
def chroma_retriever(pregunta: str, config: RunnableConfig) -> Tuple[str, List[Document]]:
    """
    Busca en los apuntes de la asignatura usando ChromaDB.
    Esta herramienta es para preguntas conceptuales, sobre el material de estudio, etc.
    El 'subject' se inyectará desde la configuración del agente, no lo provee el LLM.
    """
    subject = config["configurable"]["subject"]

    print(f"--- INFO: Usando 'ChromaDB Retriever' para la asignatura '{subject}' ---")

    chroma_path = os.path.join(BASE_CHROMA_PATH, subject)

    if not os.path.isdir(chroma_path):
        return f"Error: No se encontró la base de datos para la asignatura '{subject}'.", []

    try:
        vector_store = Chroma(persist_directory=chroma_path, embedding_function=get_embedding_function())
        retrieved_docs = vector_store.similarity_search(pregunta, k=3)

        if not retrieved_docs:
            return "No se encontraron documentos relevantes en los apuntes.", []

        context_string = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
        return f"Información encontrada en los apuntes:\n{context_string}", retrieved_docs

    except Exception as e:
        return f"Error al acceder a ChromaDB: {e}", []

# --- LÓGICA DEL GRAFO ---

def call_agent(state: AgentState):
    """Nodo del Agente. Decide si responder o usar una herramienta."""
    print("--- INFO: Agente decidiendo... ---")

    if LOCAL_INFERENCE:
        llm = ChatOpenAI(model=VLLM_MODEL_NAME, openai_api_key="EMPTY", openai_api_base=VLLM_URL, temperature=0)
    else:
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",temperature=0)

    tools = [consultar_guia_docente, chroma_retriever]
    
    llm_with_tools = llm.bind_tools(tools)

    response = llm_with_tools.invoke(state["messages"])

    # for message in state["messages"]:
    #     message.pretty_print()
        
    # response.pretty_print()
    # print("\n\n")

    return {"messages": [response]}


def execute_tools(state: AgentState) -> Dict[str, Any]:
    """
    Ejecuta las herramientas. Extrae dependencias (como 'subject') del estado
    y las inyecta en la llamada a la herramienta. Maneja correctamente la salida.
    """
    print("--- INFO: Ejecutando herramientas... ---")
    last_message = state['messages'][-1]
    tool_calls = last_message.tool_calls
    
    # Este mapa es crucial para llamar a la función correcta.
    tool_map = {"consultar_guia_docente": consultar_guia_docente, "chroma_retriever": chroma_retriever}
    
    tool_messages = []
    all_retrieved_docs = []
    
    for call in tool_calls:
        tool_name = call['name']
        print(f"--- INFO: Preparando llamada a la herramienta '{tool_name}' ---")
        
        tool_function = tool_map.get(tool_name)
        if not tool_function:
            error_message = f"Error: La herramienta '{tool_name}' no existe."
            tool_messages.append(ToolMessage(content=error_message, tool_call_id=call['id']))
            continue

        tool_args = call['args']

        try:
            content, docs = tool_function.invoke(tool_args)
            tool_messages.append(ToolMessage(content=content, tool_call_id=call['id']))
            if docs:
                all_retrieved_docs.extend(docs)
        except Exception as e:
            error_msg = f"Error al ejecutar la herramienta {tool_name}: {e}"
            print(f"--- ERROR: {error_msg} ---")
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
        content="""Eres un asistente experto. Tu trabajo es responder preguntas usando las herramientas proporcionadas.
Analiza la pregunta del usuario y usa **obligatoriamente** una de estas dos herramientas:
1. `consultar_guia_docente`: Para preguntas sobre la estructura del curso (profesores, temario, evaluación).
2. `chroma_retriever`: Para todas las demás preguntas conceptuales sobre el material de la asignatura.
Nunca respondas desde tu conocimiento previo. Siempre usa una herramienta. Una vez que la herramienta devuelva información, úsala para formular la respuesta final."""
    )
    
    # PREGUNTA DE PRUEBA
    pregunta_usuario = "¿Explícame el concepto de 'overfitting'?"
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
        print("\n--- Evento del Grafo ---")
        print(event)
        # Busca el evento final del nodo 'agent' que no tiene tool_calls
        if "agent" in event:
            last_msg = event["agent"].get("messages", [])[-1]
            if isinstance(last_msg, AIMessage) and not last_msg.tool_calls:
                 final_agent_response = last_msg

    # Mostrar la respuesta y los documentos recuperados del estado final
    if final_agent_response:
        print("\n\n--- Respuesta Final del Agente ---")
        final_agent_response.pretty_print()

    # Recupera el estado final completo para verificar los documentos
    final_state = graph.get_state(thread_config)
    final_docs = final_state.values.get('retrieved_docs')
    if final_docs:
        print("\n--- Fuentes Consultadas ---")
        for i, doc in enumerate(final_docs):
            # Asumiendo que tus metadatos tienen 'source'
            print(f"  [{i+1}] {doc.metadata.get('source', 'N/A')}")