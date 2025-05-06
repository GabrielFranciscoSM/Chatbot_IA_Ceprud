# get_embedding_function.py
from langchain_huggingface import HuggingFaceEmbeddings
import os
import torch

def get_embedding_function():
    model_path = "/app/models/models--BAAI--bge-m3"
    if os.path.exists(model_path):
        print(f"✅ Cargando modelo de embeddings desde {model_path}...")
        return HuggingFaceEmbeddings(
            model_name=model_path,
            model_kwargs={"device": "cuda" if torch.cuda.is_available() else "cpu"},
            encode_kwargs={"normalize_embeddings": True},
            local_files_only=True  # Forzar carga local
        )
    else:
        raise FileNotFoundError(f"❌ Modelo no encontrado en {model_path}.")