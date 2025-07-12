# get_embedding_function.py
import os
from langchain_openai import OpenAIEmbeddings

VLLM_URL = "http://vllm-openai-embeddings:8001/v1"  # URL del servicio de embeddings
VLLM_MODEL_NAME = "/models/BAAI--bge-m3"  # Nombre del modelo de embeddings

def get_embedding_function():
    """
    Carga la función de embeddings de Hugging Face en modo offline si los pesos
    ya están presentes en cache_folder.
    """
    return OpenAIEmbeddings(
        model=VLLM_MODEL_NAME,
        openai_api_base=VLLM_URL,
        openai_api_key="NOT_USED"
    )