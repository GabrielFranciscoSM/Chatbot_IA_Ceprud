# get_embedding_function.py
from langchain_huggingface import HuggingFaceEmbeddings
import torch

def get_embedding_function():
    """
    Retorna una función de embedding utilizando un modelo preentrenado.
    """
    # Modelo de embeddings
    model_name = "BAAI/bge-m3"
    
    # Configuración adicional para mejorar el rendimiento
    model_kwargs = {
        "device": "cuda" if torch.cuda.is_available() else "cpu",  # Usa GPU si está disponible
    }
    encode_kwargs = {
        "normalize_embeddings": True,  # Normaliza los embeddings para mejorar la similitud coseno
    }
    
    # Crea y retorna la función de embedding
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )