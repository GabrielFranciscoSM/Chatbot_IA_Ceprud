# get_embedding_function.py
from langchain_huggingface import HuggingFaceEmbeddings
import os
import torch

def get_embedding_function():
    repo_id = "BAAI/bge-m3"
    cache_dir = "/app/models"
    
    return HuggingFaceEmbeddings(
        model_name=repo_id,
        cache_folder=cache_dir,
        model_kwargs={"device": "cuda" if torch.cuda.is_available() else "cpu"},
        encode_kwargs={"normalize_embeddings": True},
        local_files_only=True
    )