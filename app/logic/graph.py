from langchain_core.documents import Document
from typing_extensions import List, TypedDict
from langgraph.graph import START, StateGraph, MessagesState
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma

from langchain_core.messages import BaseMessage,HumanMessage,AIMessage
from langgraph.checkpoint.memory import InMemorySaver

from get_embedding_function import get_embedding_function
from typing import Literal

rag_Prompt= """
            Eres un asistente para tareas de preguntas y respuestas. Utiliza los siguientes fragmentos de contexto recuperado para responder a la pregunta. Si no sabes la respuesta, simplemente di que no la sabes. Usa un máximo de tres frases y mantén la respuesta concisa.
            Pregunta: {question}
            Contexto: {context}
            Respuesta:
            """

class State(MessagesState):
    context: List[Document]
    chorma_path: str
    llm: ChatOpenAI
    use_RAG: bool
    prompt: str


def retrieve(state: State):
    print("Buscando documentos interesantes")
    # Extrae la pregunta del último mensaje en el estado
    question = state["messages"][-1].content
    print("INFO - SE USA RAG \n")
    vector_store = Chroma(persist_directory=state["chorma_path"], embedding_function=get_embedding_function())
    
    # Usa la variable 'question' para la búsqueda
    retrieved_docs = vector_store.similarity_search(question)
    print(retrieved_docs)
    return {"context": retrieved_docs}

def preparePrompt(state: State):
    if state["use_RAG"]:
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = rag_Prompt.format(question= state["messages"][-1].content, context= docs_content)
        return {"prompt": messages}
    else:
        messages = state["messages"][-1].content
        return {"prompt": messages,"context":[]}
    
    

def generate(state: State):    
    
    response = state["llm"].invoke(state["prompt"])

    return {"messages": [AIMessage(content=response.content)]}

def use_RAG(state: State)->Literal["preparePrompt", "retrieve"]:
  if state["use_RAG"]:
    return "retrieve"
  else:
    return "preparePrompt"

def buildGraph():
    graph_builder = StateGraph(State).add_sequence([retrieve,preparePrompt, generate])
    graph_builder.add_conditional_edges(START,use_RAG)
    #graph_builder.add_edge(START, )
    memory = InMemorySaver()
    return graph_builder.compile(checkpointer=memory)
