from langchain_core.documents import Document
from typing_extensions import List, TypedDict
from langgraph.graph import START, StateGraph, MessagesState
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma

from langchain_core.messages import BaseMessage,HumanMessage,AIMessage
from langgraph.checkpoint.memory import InMemorySaver

from get_embedding_function import get_embedding_function


rag_Prompt= """
            Eres un asistente para tareas de preguntas y respuestas. Utiliza los siguientes fragmentos de contexto recuperado para responder a la pregunta. Si no sabes la respuesta, simplemente di que no la sabes. Usa un máximo de tres frases y mantén la respuesta concisa.
            Pregunta: {question}
            Contexto: {context}
            Respuesta:
            """

class State(MessagesState):
    context: List[Document]
    vector_store: str
    llm: ChatOpenAI


def retrieve(state: State):
    print("Buscando documentos interesantes")
    # Extrae la pregunta del último mensaje en el estado
    question = state["messages"][-1].content
    
    
    vector_store = Chroma(collection_name="example_collection", persist_directory=state["vector_store"], embedding_function=get_embedding_function())
    
    # Usa la variable 'question' para la búsqueda
    retrieved_docs = vector_store.similarity_search(question)
    
    return {"context": retrieved_docs}


def generate(state: State):

    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = rag_Prompt.format(question= state["messages"][-1].content, context= docs_content)
    #state["messages"].append(HumanMessage(messages))
    
    response = state["llm"].invoke(messages)

    #state["messages"].append(AIMessage(content=response.content))

    for message in state["messages"]:
        message.pretty_print()

    return {"messages": [AIMessage(content=response.content)]}

def buildGraph():
    graph_builder = StateGraph(State).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    memory = InMemorySaver()
    return graph_builder.compile(checkpointer=memory)
