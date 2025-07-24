from langchain_community.vectorstores import Chroma
from ..app.RAG.get_embedding_function import get_embedding_function

CHROMA_TEST_PATH = "../app/RAG/chroma/Ingenieria del Conocimiento"

def similarity_search():
    db = Chroma(persist_directory=CHROMA_TEST_PATH, embedding_function=get_embedding_function())
    return db.similarity_search_with_score("¿Cómo instalar CLIPS en Windows?", k=5)

if __name__ == '__main__':
    result = similarity_search()
    for doc, score in results:
        print(f"Documento ({score:.4f}): {doc.page_content[:200]}...")
