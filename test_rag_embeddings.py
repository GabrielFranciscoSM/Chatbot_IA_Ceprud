from langchain_community.vectorstores import Chroma
from get_embedding_function import get_embedding_function

db = Chroma(persist_directory="chroma/Ingenieria del Conocimiento", embedding_function=get_embedding_function())
results = db.similarity_search_with_score("¿Cómo instalar CLIPS en Windows?", k=5)
for doc, score in results:
    print(f"Documento ({score:.4f}): {doc.page_content[:200]}...")