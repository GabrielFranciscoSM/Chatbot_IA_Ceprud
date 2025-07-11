# get_embedding_function.py
# from langchain_huggingface import HuggingFaceEmbeddings
import os
# import torch

# Dispositivo: 'cuda' si hay GPU, sino 'cpu'
# DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def get_embedding_function():
    """
    Carga la función de embeddings de Hugging Face en modo offline si los pesos
    ya están presentes en cache_folder.
    """
    repo_id = "BAAI/bge-m3"
    # Asumimos que los modelos están en la carpeta "models/BAAI/bge-m3"
    cache_dir = os.path.join(os.path.dirname(__file__), "models")

    # return HuggingFaceEmbeddings(
    #     model_name=repo_id,
    #     cache_folder=cache_dir,
    #     model_kwargs={"device": DEVICE},
    #     encode_kwargs={"normalize_embeddings": True}
    # )
