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
VLLM_MODEL_NAME = os.getenv("MODEL_DIR", "/models/Sreenington--Phi-3-mini-4k-instruct-AWQ")
BASE_CHROMA_PATH = "../RAG" + os.getenv("BASE_CHROMA_PATH", "chroma")

LOCAL_INFERENCE=False

# Estado del agente, incluyendo los documentos recuperados y la asignatura
class AgentState(MessagesState):
    retrieved_docs: List[Document]
    subject: str # El campo para saber qué base de datos Chroma usar

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

        # Rutas posibles para el archivo de guía docente
        possible_paths = [
            os.path.join("app", "rag", "data", subject, "guía_docente.json"),
            os.path.join("app", "rag", "data", subject, "guia_docente.json"),
            os.path.join("rag", "data", subject, "guía_docente.json"),
            os.path.join("rag", "data", subject, "guia_docente.json")
        ]
        
        # Obtener directorio actual
        current_dir = os.getcwd()
        
        # Buscar el archivo
        path = None
        for test_path in possible_paths:
            abs_path = os.path.abspath(test_path)
            if os.path.exists(abs_path):
                path = abs_path
                break
        
        if not path:
            error_msg = f"No se encontró archivo de guía docente para '{subject}'"
            return error_msg, []
            
        # Cargar el JSON
        with open(path, 'r', encoding='utf-8') as f:
            guia = json.load(f)
        
        # Mapeo de secciones
        seccion_mapping = {
            "profesorado": "profesorado_y_tutorias",
            "profesores": "profesorado_y_tutorias", 
            "tutorias": "profesorado_y_tutorias",
            "evaluacion": "evaluación",
            "evaluación": "evaluación",
            "examen": "evaluación",
            "examenes": "evaluación",
            "temario": "programa_de_contenidos_teóricos_y_prácticos",
            "programa": "programa_de_contenidos_teóricos_y_prácticos",
            "contenidos": "programa_de_contenidos_teóricos_y_prácticos",
            "temas": "programa_de_contenidos_teóricos_y_prácticos",
            "metodologia": "metodología_docente",
            "metodología": "metodología_docente",
            "bibliografia": "bibliografía",
            "bibliografía": "bibliografía",
            "libros": "bibliografía",
            "prerrequisitos": "prerrequisitos_o_recomendaciones",
            "recomendaciones": "prerrequisitos_o_recomendaciones",
            "competencias": "resultados_del_proceso_de_formación_y_de_aprendizaje",
            "resultados": "resultados_de_aprendizaje",
            "enlaces": "enlaces_recomendados",
            "recursos": "enlaces_recomendados",
            "informacion_adicional": "información_adicional",
            "información_adicional": "información_adicional"
        }
        
        seccion_limpia = seccion.lower().strip()
        
        # Buscar mapeo exacto
        target_key = seccion_mapping.get(seccion_limpia)
        
        if target_key and target_key in guia:
            resultado = {target_key: guia[target_key]}
            result_json = json.dumps(resultado, ensure_ascii=False, indent=2)
            return result_json, []
        
        # Búsqueda parcial
        for key in guia.keys():
            if seccion_limpia in key.lower():
                resultado = {key: guia[key]}
                return json.dumps(resultado, ensure_ascii=False, indent=2), []
        
        # No encontrado
        secciones_disponibles = list(guia.keys())
        error_msg = f"Error: La sección '{seccion}' no se encontró.\n\nSecciones disponibles:\n" + \
                   "\n".join([f"- {s}" for s in secciones_disponibles])
        return error_msg, []
        
    except Exception as e:
        error_msg = f"Error en consultar_guia_docente: {str(e)}"
        return error_msg, []


@tool
def chroma_retriever(pregunta: str, config: RunnableConfig) -> Tuple[str, List[Document]]:
    """
    Busca en los apuntes de la asignatura usando ChromaDB.
    Esta herramienta es para preguntas conceptuales, sobre el material de estudio, etc.
    El 'subject' se inyectará desde la configuración del agente, no lo provee el LLM.
    """
    try:
        subject = config["configurable"]["subject"]

        # Get current working directory and script directory
        current_dir = os.getcwd()
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # List possible paths to search for ChromaDB
        possible_paths = [
            # Absolute paths (container environments)
            f"/chatbot/app/rag/chroma/{subject}",
            f"/app/rag/chroma/{subject}",
            
            # Relative paths from current directory
            os.path.join("app", "rag", "chroma", subject),
            os.path.join("rag", "chroma", subject),
            os.path.join(".", "app", "rag", "chroma", subject),
            os.path.join(".", "rag", "chroma", subject),
            
            # Paths relative to script directory
            os.path.join(script_dir, "..", "..", "rag", "chroma", subject),
            os.path.join(script_dir, "..", "rag", "chroma", subject),
            
            # Using BASE_CHROMA_PATH
            os.path.join(BASE_CHROMA_PATH, subject),
            os.path.abspath(os.path.join(BASE_CHROMA_PATH, subject)),
        ]
        
        chroma_path = None
        for i, test_path in enumerate(possible_paths):
            abs_path = os.path.abspath(test_path)
            
            if os.path.exists(abs_path):
                if os.path.isdir(abs_path):
                    chroma_path = abs_path
                    break

        if not chroma_path:
            error_msg = f"No se encontró la base de datos ChromaDB para la asignatura '{subject}'"
            return error_msg, []

        vector_store = Chroma(persist_directory=chroma_path, embedding_function=get_embedding_function())

        # 3. Query expansion - Simple synonym addition
        expanded_queries = [pregunta]
        # Add simple expansions for common technical terms
        expansions = {
            "algoritmo": ["método", "técnica", "procedimiento"],
            "metaheurística": ["metaheurísticas", "heurística", "optimización"],
            "evaluación": ["evaluacion", "examen", "prueba"],
            "implementación": ["implementacion", "código", "programación"],
            "ejemplo": ["ejemplos", "caso", "aplicación"]
        }
        
        pregunta_lower = pregunta.lower()
        for term, synonyms in expansions.items():
            if term in pregunta_lower:
                for synonym in synonyms:
                    expanded_queries.append(pregunta.replace(term, synonym))

        # Get results from all expanded queries
        all_docs = []
        for query in expanded_queries[:3]:  # Limit to avoid too many calls
            docs = vector_store.similarity_search_with_score(query, k=6)
            all_docs.extend(docs)

        if not all_docs:
            return "No se encontraron documentos relevantes en los apuntes.", []

        # 1. Adaptive threshold tuning
        scores = [score for _, score in all_docs]
        if scores:
            avg_score = sum(scores) / len(scores)
            std_score = (sum((s - avg_score) ** 2 for s in scores) / len(scores)) ** 0.5
            # Use mean - 0.5*std as threshold to keep better half
            adaptive_threshold = max(avg_score - 0.5 * std_score, 0.5)
        else:
            adaptive_threshold = 0.7

        # Filter by adaptive threshold
        filtered_docs = [(doc, score) for doc, score in all_docs if score < adaptive_threshold]

        # 4. Simple metadata filtering (if available)
        # Priority to docs with certain metadata patterns
        priority_docs = []
        regular_docs = []
        
        for doc, score in filtered_docs:
            metadata = doc.metadata
            # Prioritize docs with specific metadata
            if any(key in metadata for key in ['chapter', 'section', 'title', 'topic']):
                priority_docs.append((doc, score))
            else:
                regular_docs.append((doc, score))

        # Combine prioritized and regular docs
        sorted_docs = priority_docs + regular_docs

        # Remove duplicates based on content similarity
        unique_docs = []
        seen_content = set()
        
        for doc, score in sorted_docs:
            # Simple deduplication based on first 100 chars
            content_signature = doc.page_content[:100].strip()
            if content_signature not in seen_content:
                seen_content.add(content_signature)
                unique_docs.append((doc, score))

        # 2. Simple reranking based on keyword overlap and content quality
        pregunta_words = set(pregunta.lower().split())
        reranked_docs = []
        
        for doc, original_score in unique_docs:
            content_lower = doc.page_content.lower()
            
            # Keyword overlap score
            doc_words = set(content_lower.split())
            keyword_overlap = len(pregunta_words.intersection(doc_words))
            
            # Content quality score
            content_length = len(doc.page_content)
            length_score = 1.0 if 100 <= content_length <= 1500 else 0.5
            
            # Has structured content (headings, lists, etc.)
            structure_score = 1.2 if any(marker in content_lower for marker in [':', '•', '-', '1.', '2.']) else 1.0
            
            # Combined reranking score (lower is better)
            rerank_score = original_score - (keyword_overlap * 0.1) - (length_score * 0.05) - (structure_score * 0.02)
            
            reranked_docs.append((doc, rerank_score, original_score))

        # Sort by reranked score and take top results
        reranked_docs.sort(key=lambda x: x[1])
        final_docs = [doc for doc, _, _ in reranked_docs[:4]]

        # Enhanced formatting with metadata
        context_parts = []
        for i, doc in enumerate(final_docs):
            # Extract useful metadata for context
            source_info = ""
            if 'source' in doc.metadata:
                source_info = f" (Fuente: {doc.metadata['source']})"
            elif 'filename' in doc.metadata:
                source_info = f" (Archivo: {doc.metadata['filename']})"
            elif 'chapter' in doc.metadata:
                source_info = f" (Capítulo: {doc.metadata['chapter']})"
                
            context_parts.append(f"[Documento {i+1}]{source_info}:\n{doc.page_content}")
        
        context_string = "\n\n---\n\n".join(context_parts)
        result_message = f"Información encontrada en los apuntes:\n\n{context_string}"
        
        return result_message, final_docs

    except Exception as e:
        error_msg = f"Error en chroma_retriever: {str(e)}"
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