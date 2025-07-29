# from langchain_core.documents import Document
# from typing_extensions import List, TypedDict
# from langgraph.graph import START, StateGraph, MessagesState
# from langgraph.graph.message import add_messages
# from langchain_openai import ChatOpenAI
# from langchain_chroma import Chroma

# from langchain_core.messages import BaseMessage,HumanMessage,AIMessage
# from langgraph.checkpoint.memory import InMemorySaver

# from get_embedding_function import get_embedding_function
# from typing import Literal

# import os
# from dotenv import load_dotenv
# load_dotenv()

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

# rag_Prompt= """
#             Eres un asistente para tareas de preguntas y respuestas. Utiliza los siguientes fragmentos de contexto recuperado para responder a la pregunta. Si no sabes la respuesta, simplemente di que no la sabes.
#             Pregunta: {question}
#             Contexto: {context}
#             Respuesta:
#             """

# MAX_HISTORY_LENGTH = 7

# class State(MessagesState):
#     context: List[Document]
#     chorma_path: str
#     llm: ChatOpenAI
#     use_RAG: bool
#     prompt: str


# def retrieve(state: State):
#     print("Buscando documentos interesantes")
#     # Extrae la pregunta del último mensaje en el estado
#     question = state["messages"][-1].content
#     print("INFO - SE USA RAG \n")
#     vector_store = Chroma(persist_directory=state["chorma_path"], embedding_function=get_embedding_function())
    
#     # Usa la variable 'question' para la búsqueda
#     docs_and_scores = vector_store.similarity_search_with_score(question, k=5)    
#     retrieved_docs, _ = zip(*docs_and_scores)

#     #retrieved_docs = vector_store.similarity_search(question)
    
#     print(retrieved_docs)
#     return {"context": retrieved_docs}

# def preparePrompt(state: State):
#     if state["use_RAG"]:
#         #context = "\n\n---\n\n".join(d.page_content for d in docs)

#         docs_content = "\n\n---\n\n".join(doc.page_content for doc in state["context"])

#         print("CONTEXT:\n" + docs_content + "\n")

#         messages = rag_Prompt.format(question= state["messages"][-1].content, context= docs_content)
#         return {"prompt": messages}
#     else:
#         messages = state["messages"][-1].content
#         return {"prompt": messages,"context":[]}
    
    

# def generate(state: State):    
#     response = state["llm"].invoke(state["prompt"])

#     return {"messages": [AIMessage(content=response.content)]}

# def use_RAG(state: State)->Literal["preparePrompt", "retrieve"]:
#   if state["use_RAG"]:
#     return "retrieve"
#   else:
#     return "preparePrompt"

# def buildGraph():
#     graph_builder = StateGraph(State).add_sequence([retrieve, preparePrompt, generate])
#     graph_builder.add_conditional_edges(START,use_RAG)
#     memory = InMemorySaver()
#     return graph_builder.compile(checkpointer=memory)



import json
from langchain_core.documents import Document
from typing_extensions import TypedDict, List
from langgraph.graph import END, StateGraph, MessagesState
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI # Mantenemos la importación por si cambias
# Cambia esta línea si usas Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.tools import tool, Tool
from langgraph.prebuilt import ToolNode

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from get_embedding_function import get_embedding_function # Asegúrate de que esta función exista
from typing import Literal

import os
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY


# --- 2. ESTADO DEL GRAFO (STATE) ---
class State(MessagesState):
     chorma_path: str
     use_RAG:bool

# --- 1. DEFINIR LAS HERRAMIENTAS (TOOLS) ---

@tool
def consultar_guia_docente(seccion: str) -> str:
    """
    Consulta secciones específicas de la guía docente de la asignatura. 
    Es la mejor opción para preguntas concretas y estructuradas sobre: 'profesorado_y_tutorias', 
    'prerrequisitos_o_recomendaciones', 'breve_descripción_de_contenidos', 'competencias', 
    'resultados_de_aprendizaje', 'programa_de_contenidos_teóricos_y_prácticos', 'bibliografía', 
    'enlaces_recomendados', 'metodología_docente', 'evaluación'.
    """
    print(f"--- INFO: Usando herramienta Guía Docente para la sección: {seccion} ---")
    try:
        # Asume que el JSON de la guía anterior está en el mismo directorio
        with open('guia_docente_de_modelos_avanzados.json', 'r', encoding='utf-8') as f:
            guia = json.load(f)
    except FileNotFoundError:
        return json.dumps({"error": "El archivo de la guía docente no se encontró."})
    
    seccion_limpia = seccion.lower().strip().replace(' ', '_')
    
    # Búsqueda por coincidencia parcial para dar flexibilidad
    for key in guia.keys():
        if seccion_limpia in key:
            # --- CORRECCIÓN AQUÍ: Devolver un string JSON, no un diccionario ---
            return json.dumps({key: guia[key]}, ensure_ascii=False, indent=2)
            
    return json.dumps({"error": f"La sección '{seccion}' no se encontró en la guía docente."})


@tool
def chroma_retriever(pregunta: str, state: State) -> str:
    """
    Busca en la base de datos documental (ChromaDB) para encontrar información relevante.
    Es la mejor opción para preguntas generales, conceptuales, o que requieran buscar 
    en apuntes, PDFs u otros documentos de la asignatura.
    """
    print(f"--- INFO: Usando herramienta ChromaDB Retriever para la pregunta: {pregunta} ---")
    try:
        CHROMA_PATH = state["chorma_path"] # Asegúrate de que esta ruta es correcta
        vector_store = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embedding_function())
        
        retrieved_docs = vector_store.similarity_search(pregunta, k=3)
        
        # --- CORRECCIÓN AQUÍ: Devolver un string formateado, no una lista de Documentos ---
        if not retrieved_docs:
            return "No se encontraron documentos relevantes en ChromaDB."
        
        context_string = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
        return context_string
    except Exception as e:
        return f"Error al acceder a ChromaDB: {e}"


# NODO 1: El agente que decide la herramienta
def call_agent(state: State, llm: ChatGoogleGenerativeAI, tools: List[Tool]):
    print("--- INFO: Agente [1]: Decidiendo herramienta... ---")
    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# NODO 2: El generador que sintetiza la respuesta final
def generate_final_response(state: State, llm: ChatGoogleGenerativeAI):
    print("--- INFO: Agente [2]: Generando respuesta final... ---")
    # Extraemos la pregunta original y el resultado de la herramienta
    human_question = state["messages"][0].content
    tool_result = state["messages"][-1].content
    
    # Creamos un prompt simple y directo
    prompt = f"""
    Basándote en la siguiente información recuperada por una herramienta, responde a la pregunta original del usuario.
    Sé claro y conciso.

    Información Recuperada:
    {tool_result}

    Pregunta Original del Usuario:
    {human_question}

    Respuesta:
    """
    # Invocamos el LLM de forma simple, sin modo agente

    print("\n" + prompt + "\n")

    response = llm.invoke(prompt)
    return {"messages": [response]}


# ROUTER: Decide el camino a seguir
def should_use_tool(state: State) -> Literal["tools", "end_without_tools"]:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        print("--- INFO: Router -> Herramienta necesaria. ---")
        return "tools"
    else:
        print("--- INFO: Router -> No se necesita herramienta. Respondiendo directamente. ---")
        return "end_without_tools"

# --- 3. CONSTRUCCIÓN DEL GRAFO ---
def buildGraph():
    # Usamos Gemini Flash, que es rápido y excelente para estas tareas
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    tools = [consultar_guia_docente, chroma_retriever]
    tool_node = ToolNode(tools)

    # Nodos del grafo
    agent_node = lambda state: call_agent(state, llm, tools)
    final_response_node = lambda state: generate_final_response(state, llm)
    
    graph_builder = StateGraph(State)
    graph_builder.add_node("agent", agent_node)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_node("final_answer_generator", final_response_node)

    graph_builder.set_entry_point("agent")

    # Conexiones lógicas
    graph_builder.add_conditional_edges(
        "agent",
        should_use_tool,
        {
            "tools": "tools",
            "end_without_tools": END # Si el agente responde directamente, termina.
        },
    )
    # Después de usar la herramienta, vamos al generador final, no de vuelta al agente
    graph_builder.add_edge("tools", "final_answer_generator")
    graph_builder.add_edge("final_answer_generator", END)

    memory = InMemorySaver()
    return graph_builder.compile(checkpointer=memory)

# --- 4. EJEMPLO DE USO ---
if __name__ == '__main__':
    graph = buildGraph()
    thread_config = {"configurable": {"thread_id": "mi_conversacion_gemini_4"}}
    pregunta_guia = "que es un algoritmo greedy?"
    
    print(f"\n--- Preguntando: {pregunta_guia} ---")
    events = graph.stream(
        {"messages": [HumanMessage(content=pregunta_guia)]},
        config=thread_config,
    )
    for event in events:
        # Imprimimos la respuesta final
        if "final_answer_generator" in event:
            event["final_answer_generator"]["messages"][-1].pretty_print()