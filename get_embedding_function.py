# get_embedding_function.py
from langchain_huggingface import HuggingFaceEmbeddings
import os
import torch

def get_embedding_function():
    """
    Retorna una función de embedding utilizando un modelo preentrenado.
    Si el modelo ya existe en /app/models, se carga desde allí.
    De lo contrario, se descarga automáticamente.
    """
    model_path = "/app/models/models--BAAI--bge-m3"
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"❌ Modelo no encontrado en {model_path}. Descarga el modelo primero.")
    
    print(f"✅ Cargando modelo existente desde {model_path}...")
    return HuggingFaceEmbeddings(
        model_name=model_path,
        model_kwargs={"device": "cuda" if torch.cuda.is_available() else "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )