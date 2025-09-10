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
        print(f"[DEBUG GUIA] === INICIANDO consultar_guia_docente ===")
        print(f"[DEBUG GUIA] TIMESTAMP BUILD: 2025-09-09 11:30:00")
        print(f"[DEBUG GUIA] Sección solicitada: '{seccion}'")
        
        # CORRECTO: Extraer subject desde el config
        subject = config["configurable"]["subject"]
        print(f"[DEBUG GUIA] Asignatura: '{subject}'")

        # Rutas posibles para el archivo de guía docente
        possible_paths = [
            os.path.join("app", "rag", "data", subject, "guía_docente.json"),
            os.path.join("app", "rag", "data", subject, "guia_docente.json"),
            os.path.join("rag", "data", subject, "guía_docente.json"),
            os.path.join("rag", "data", subject, "guia_docente.json")
        ]
        
        # Obtener directorio actual y script
        current_dir = os.getcwd()
        # Nota: __file__ puede no funcionar en todos los entornos (ej. notebooks)
        # script_dir = os.path.dirname(os.path.abspath(__file__)) 
        print(f"[DEBUG GUIA] Directorio actual: {current_dir}")
        
        # Buscar el archivo
        path = None
        for test_path in possible_paths:
            abs_path = os.path.abspath(test_path)
            print(f"[DEBUG GUIA] Probando: {abs_path}")
            if os.path.exists(abs_path):
                path = abs_path
                print(f"[DEBUG GUIA] ✅ Archivo encontrado: {path}")
                break
            else:
                print(f"[DEBUG GUIA] ❌ No existe: {abs_path}")
        
        if not path:
            error_msg = f"[ERROR] No se encontró archivo de guía docente para '{subject}'. Directorio actual: {current_dir}"
            print(error_msg)
            return error_msg, []
            
        # Cargar el JSON
        print(f"[DEBUG GUIA] Cargando JSON desde: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            guia = json.load(f)
        print(f"[DEBUG GUIA] ✅ JSON cargado con {len(guia)} claves")
        
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
        print(f"[DEBUG GUIA] Sección limpia: '{seccion_limpia}'")
        
        # Buscar mapeo exacto
        target_key = seccion_mapping.get(seccion_limpia)
        print(f"[DEBUG GUIA] Mapeo encontrado: '{target_key}'")
        
        if target_key and target_key in guia:
            print(f"[DEBUG GUIA] ✅ Clave encontrada en JSON: {target_key}")
            resultado = {target_key: guia[target_key]}
            result_json = json.dumps(resultado, ensure_ascii=False, indent=2)
            print(f"[DEBUG GUIA] ✅ Resultado generado ({len(result_json)} caracteres)")
            return result_json, []
        
        # Búsqueda parcial
        print(f"[DEBUG GUIA] Búsqueda parcial en claves: {list(guia.keys())}")
        for key in guia.keys():
            if seccion_limpia in key.lower():
                print(f"[DEBUG GUIA] ✅ Coincidencia parcial encontrada: {key}")
                resultado = {key: guia[key]}
                return json.dumps(resultado, ensure_ascii=False, indent=2), []
        
        # No encontrado
        secciones_disponibles = list(guia.keys())
        error_msg = f"Error: La sección '{seccion}' no se encontró.\n\nSecciones disponibles:\n" + \
                   "\n".join([f"- {s}" for s in secciones_disponibles])
        print(f"[DEBUG GUIA] ❌ {error_msg}")
        return error_msg, []
        
    except Exception as e:
        error_msg = f"[ERROR CRÍTICO] Error en consultar_guia_docente: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return error_msg, []


@tool
def chroma_retriever(pregunta: str, config: RunnableConfig) -> Tuple[str, List[Document]]:
    """
    Busca en los apuntes de la asignatura usando ChromaDB.
    Esta herramienta es para preguntas conceptuales, sobre el material de estudio, etc.
    El 'subject' se inyectará desde la configuración del agente, no lo provee el LLM.
    """
    try:
        print(f"[DEBUG CHROMA] === INICIANDO chroma_retriever ===")
        print(f"[DEBUG CHROMA] TIMESTAMP BUILD: 2025-09-10 12:00:00")
        print(f"[DEBUG CHROMA] Pregunta: '{pregunta}'")
        
        # Extract subject from config
        subject = config["configurable"]["subject"]
        print(f"[DEBUG CHROMA] Asignatura: '{subject}'")

        # Get current working directory and script directory
        current_dir = os.getcwd()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"[DEBUG CHROMA] Directorio actual: {current_dir}")
        print(f"[DEBUG CHROMA] Directorio del script: {script_dir}")
        print(f"[DEBUG CHROMA] BASE_CHROMA_PATH: {BASE_CHROMA_PATH}")

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

        print(f"[DEBUG CHROMA] Probando {len(possible_paths)} rutas posibles:")
        
        chroma_path = None
        for i, test_path in enumerate(possible_paths):
            abs_path = os.path.abspath(test_path)
            print(f"[DEBUG CHROMA] [{i+1}] Probando: {abs_path}")
            
            if os.path.exists(abs_path):
                if os.path.isdir(abs_path):
                    chroma_path = abs_path
                    print(f"[DEBUG CHROMA] ✅ Directorio encontrado: {chroma_path}")
                    
                    # List contents of the directory
                    try:
                        contents = os.listdir(chroma_path)
                        print(f"[DEBUG CHROMA] Contenido del directorio ({len(contents)} elementos):")
                        for item in contents[:10]:  # Show first 10 items
                            item_path = os.path.join(chroma_path, item)
                            item_type = "DIR" if os.path.isdir(item_path) else "FILE"
                            print(f"[DEBUG CHROMA]   - {item} ({item_type})")
                        if len(contents) > 10:
                            print(f"[DEBUG CHROMA]   ... y {len(contents) - 10} elementos más")
                    except Exception as e:
                        print(f"[DEBUG CHROMA] Error listando contenido: {e}")
                    
                    break
                else:
                    print(f"[DEBUG CHROMA] ❌ Existe pero no es directorio: {abs_path}")
            else:
                print(f"[DEBUG CHROMA] ❌ No existe: {abs_path}")

        if not chroma_path:
            error_msg = f"[ERROR CHROMA] No se encontró la base de datos ChromaDB para la asignatura '{subject}'."
            print(error_msg)
            print(f"[DEBUG CHROMA] Directorio actual: {current_dir}")
            print(f"[DEBUG CHROMA] Estructura del directorio actual:")
            try:
                for root, dirs, files in os.walk(current_dir):
                    level = root.replace(current_dir, '').count(os.sep)
                    indent = ' ' * 2 * level
                    print(f"{indent}{os.path.basename(root)}/")
                    subindent = ' ' * 2 * (level + 1)
                    for file in files[:5]:  # Limit to 5 files per directory
                        print(f"{subindent}{file}")
                    if len(files) > 5:
                        print(f"{subindent}... y {len(files) - 5} archivos más")
                    if level > 3:  # Limit depth
                        break
            except Exception as e:
                print(f"[DEBUG CHROMA] Error explorando estructura: {e}")
            
            return error_msg, []

        print(f"[DEBUG CHROMA] Usando ChromaDB en: {chroma_path}")

        # Initialize ChromaDB
        print(f"[DEBUG CHROMA] Inicializando ChromaDB...")
        vector_store = Chroma(persist_directory=chroma_path, embedding_function=get_embedding_function())
        print(f"[DEBUG CHROMA] ✅ ChromaDB inicializado correctamente")

        # Perform similarity search
        print(f"[DEBUG CHROMA] Realizando búsqueda de similitud (k=3)...")
        print(f"[DEBUG CHROMA] Pregunta: {pregunta}")
        retrieved_docs = vector_store.similarity_search(pregunta, k=3)
        print(f"[DEBUG CHROMA] ✅ Búsqueda completada. Documentos encontrados: {len(retrieved_docs)}")

        if not retrieved_docs:
            print(f"[DEBUG CHROMA] ❌ No se encontraron documentos relevantes")
            return "No se encontraron documentos relevantes en los apuntes.", []

        # Process results
        print(f"[DEBUG CHROMA] Procesando resultados:")
        for i, doc in enumerate(retrieved_docs):
            print(f"[DEBUG CHROMA] Documento {i+1}:")
            print(f"[DEBUG CHROMA]   - Longitud: {len(doc.page_content)} caracteres")
            print(f"[DEBUG CHROMA]   - Metadatos: {doc.metadata}")
            print(f"[DEBUG CHROMA]   - Chunk: {doc.page_content}...")

        context_string = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
        result_message = f"Información encontrada en los apuntes:\n{context_string}"
        
        print(f"[DEBUG CHROMA] ✅ Resultado generado ({len(result_message)} caracteres)")
        return result_message, retrieved_docs

    except Exception as e:
        error_msg = f"[ERROR CRÍTICO CHROMA] Error en chroma_retriever: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return error_msg, []

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
- NUNCA respondas desde tu conocimiento previo sin usar herramientas
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