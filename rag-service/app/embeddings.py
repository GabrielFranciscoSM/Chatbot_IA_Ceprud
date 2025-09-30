# get_embedding_function.py
import os
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# URLs del servicio de embeddings - pueden ser diferentes en el RAG service
VLLM_URL = os.getenv("VLLM_EMBEDDING_URL","http://vllm-openai-embeddings:8001") + "/v1"
VLLM_MODEL_NAME = os.getenv("EMBEDDING_MODEL_DIR","/models/Qwen--Qwen3-Embedding-0.6B")

def get_embedding_function():
    """
    Carga la función de embeddings para el RAG Service.
    Utiliza el servicio vLLM de embeddings.
    """
    return OpenAIEmbeddings(
        model=VLLM_MODEL_NAME,
        openai_api_base=VLLM_URL,
        openai_api_key="NOT_USED"
    )