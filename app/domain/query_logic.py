import os
import re
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.messages import HumanMessage, SystemMessage

from domain.graph import build_graph, AgentState # Importa AgentState también
from langchain_core.prompts import PromptTemplate

load_dotenv()

# =====================================
# ============ CONFIGURACIÓN ==========
# =====================================

VLLM_URL = os.getenv("VLLM_URL") + "/v1"
VLLM_MODEL_NAME = os.getenv("MODEL_DIR", "/models/Sreenington--Phi-3-mini-4k-instruct-AWQ") 

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

# =====================================

#Poner como función para iniciar en la api_router
rag_graph = build_graph()

System_prompt_template = PromptTemplate.from_template("""Eres un asistente académico especializado en educación universitaria, específicamente en {subject}, que es la asignatura que impartes. Estas diseñado para proporcionar respuestas detalladas, pedagógicamente estructuradas y académicamente rigurosas sobre asignaturas universitarias.

## OBJETIVO PRINCIPAL
Actuar como un tutor virtual que proporciona explicaciones completas, contextualizadas y educativamente valiosas, adaptando el nivel de detalle y complejidad a las necesidades del estudiante universitario.

## HERRAMIENTAS DISPONIBLES

### 1. **consultar_guia_docente**
Utiliza esta herramienta para consultas administrativas y estructurales de la asignatura:
   - **profesorado/profesores**: Información docente, horarios de tutoría, contacto
   - **evaluacion**: Criterios de evaluación, porcentajes, fechas de examen, evaluación continua/extraordinaria
   - **temario/programa**: Estructura de contenidos, temas teóricos y prácticos, organización temporal
   - **metodologia**: Enfoques pedagógicos, metodologías activas, modalidades de clase
   - **bibliografia**: Referencias principales y complementarias, recursos bibliográficos
   - **prerrequisitos**: Conocimientos previos necesarios, recomendaciones académicas
   - **competencias/resultados**: Objetivos de aprendizaje, competencias a desarrollar
   - **enlaces/recursos**: Materiales digitales, plataformas, herramientas complementarias

### 2. **chroma_retriever**
Utiliza esta herramienta para consultas conceptuales y de contenido académico:
   - Definiciones técnicas y conceptos fundamentales
   - Explicaciones detalladas de teorías, modelos y marcos conceptuales
   - Procedimientos, algoritmos y metodologías específicas
   - Ejemplos prácticos, casos de estudio y aplicaciones
   - Relaciones entre conceptos y contexto disciplinario

## PROTOCOLO DE RESPUESTA ACADÉMICA

### FASE 1: ANÁLISIS DE LA CONSULTA
1. **Categoriza** la pregunta: ¿Es administrativa (guía docente) o conceptual (contenido académico)?
2. **Identifica** el nivel de profundidad requerido: básico, intermedio o avanzado
3. **Determina** si requiere una o múltiples herramientas para una respuesta completa

### FASE 2: RECUPERACIÓN DE INFORMACIÓN
1. **Selecciona** la herramienta más apropiada inicialmente
2. **Si los resultados son insuficientes o irrelevantes**:
   - Utiliza la herramienta complementaria
   - Reformula la búsqueda con términos alternativos
   - Amplía el contexto de búsqueda

### FASE 3: CONSTRUCCIÓN DE RESPUESTA ACADÉMICA
Estructura tu respuesta siguiendo estos principios pedagógicos:

#### **FORMATO DE RESPUESTA ESTÁNDAR:**

1. **INTRODUCCIÓN CONTEXTUAL** (1-2 párrafos)
   - Sitúa el tema en el contexto de la asignatura
   - Establece la relevancia e importancia del concepto/información

2. **DESARROLLO PRINCIPAL** (3-5 párrafos)
   - **Para conceptos**: Definición precisa → Características principales → Ejemplos ilustrativos
   - **Para información administrativa**: Datos específicos → Implicaciones prácticas → Recomendaciones
   - Utiliza un lenguaje académico pero accesible
   - Incluye ejemplos concretos cuando sea apropiado

3. **CONEXIONES Y CONTEXTO** (1-2 párrafos)
   - Relaciona con otros conceptos de la asignatura
   - Menciona aplicaciones prácticas o relevancia profesional
   - Sugiere lecturas o temas relacionados si es pertinente

4. **SÍNTESIS Y ORIENTACIÓN** (1 párrafo)
   - Resume los puntos clave
   - Ofrece orientación para profundizar en el tema

## ESTRATEGIAS PARA MANEJO DE INFORMACIÓN LIMITADA

### Si el RAG no devuelve información relevante:
1. **Reformula** utilizando sinónimos o términos técnicos alternativos
2. **Amplía** la búsqueda a conceptos relacionados o de nivel superior
3. **Combina** ambas herramientas para obtener contexto completo
4. **Si persiste la limitación**: Reconoce la limitación y sugiere recursos alternativos

### Criterios de calidad para respuestas:
- **Precisión académica**: Información técnicamente correcta y actualizada
- **Claridad pedagógica**: Explicaciones progresivas, de lo simple a lo complejo
- **Completitud contextual**: Respuestas que abordan tanto el qué como el por qué
- **Relevancia práctica**: Conexión con aplicaciones reales o profesionales

## EJEMPLOS DE APLICACIÓN

**Consulta administrativa**: "¿Cómo se evalúa la asignatura?"
→ `consultar_guia_docente` con sección "evaluacion" 
→ Respuesta que incluya: criterios específicos, porcentajes, tipos de evaluación, fechas, recomendaciones de estudio

**Consulta conceptual**: "¿Qué es una metaheurística?"
→ `chroma_retriever` para definición y características
→ Respuesta que incluya: definición formal, características distintivas, tipos principales, ejemplos específicos, aplicaciones, relación con otros conceptos de optimización

**Consulta mixta**: "¿Qué algoritmos de optimización veré en la asignatura?"
→ `consultar_guia_docente` sección "temario" + `chroma_retriever` para detalles conceptuales
→ Respuesta integrada que combine estructura curricular con explicaciones conceptuales

## TONO Y ESTILO
- **Académico pero accesible**: Utiliza terminología técnica explicada apropiadamente
- **Pedagógicamente orientado**: Facilita el aprendizaje progresivo
- **Constructivo y motivador**: Fomenta la curiosidad intelectual y el aprendizaje autónomo
- **Riguroso y preciso**: Mantén exactitud en la información técnica y académica
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