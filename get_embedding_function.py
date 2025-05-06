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
    # Modelo de embeddings
    model_name = "BAAI/bge-m3"
    model_path = "/app/models/BAAI-bge-m3"  # Ruta dentro del contenedor
    
    # Verifica si el modelo ya está descargado
    if not os.path.exists(model_path):
        print(f"🌟 Descargando modelo {model_name} a {model_path}...")
        model_kwargs = {
            "device": "cuda" if torch.cuda.is_available() else "cpu",  # Usa GPU si está disponible
        }
        encode_kwargs = {
            "normalize_embeddings": True,  # Normaliza los embeddings para mejorar la similitud coseno
        }
        # Descarga el modelo desde Hugging Face Hub
        return HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs,
            cache_folder="/app/models"  # Almacena el modelo en /app/models
        )
    else:
        print(f"✅ Cargando modelo existente desde {model_path}...")
        model_kwargs = {
            "device": "cuda" if torch.cuda.is_available() else "cpu",  # Usa GPU si está disponible
        }
        encode_kwargs = {
            "normalize_embeddings": True,  # Normaliza los embeddings para mejorar la similitud coseno
        }
        # Carga el modelo desde la ruta local
        return HuggingFaceEmbeddings(
            model_name=model_path,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )