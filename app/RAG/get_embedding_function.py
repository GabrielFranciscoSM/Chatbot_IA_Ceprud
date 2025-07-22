# get_embedding_function.py
import os
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

VLLM_URL = "http://vllm-openai-embeddings:8001/v1"  # URL del servicio de embeddings
VLLM_MODEL_NAME = "/models/Qwen--Qwen3-Embedding-0.6B"  # Nombre del modelo de embeddings

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

def get_embedding_function():
    """
    Carga la función de embeddings de Hugging Face en modo offline si los pesos
    ya están presentes en cache_folder.
    """

    # embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-exp-03-07")
    return OpenAIEmbeddings(
        model=VLLM_MODEL_NAME,
        openai_api_base=VLLM_URL,
        openai_api_key="NOT_USED"
    )