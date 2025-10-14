# get_embedding_function.py
import os
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# URLs del servicio de embeddings - pueden ser diferentes en el RAG service
VLLM_URL = os.getenv("VLLM_EMBEDDING_URL","http://vllm-openai-embeddings:8001") + "/v1"
VLLM_MODEL_NAME = os.getenv("EMBEDDING_MODEL_DIR","/models/Qwen--Qwen3-Embedding-0.6B")

# Ollama configuration for CPU fallback
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "nomic-embed-text")
USE_OLLAMA = os.getenv("USE_OLLAMA", "true").lower() == "true"

def get_embedding_function():
    """
    Carga la función de embeddings para el RAG Service.
    Utiliza el servicio vLLM de embeddings (GPU) o Ollama (CPU) dependiendo de la configuración.
    """
    if USE_OLLAMA:
        # Use Ollama for CPU-based embeddings
        try:
            from langchain_ollama import OllamaEmbeddings
            return OllamaEmbeddings(
                model=OLLAMA_MODEL_NAME,
                base_url=OLLAMA_URL,
                # Note: num_ctx and num_thread are configured via Ollama server
                # using OLLAMA_NUM_PARALLEL environment variable in docker-compose
            )
        except ImportError:
            raise ImportError(
                "langchain-ollama is not installed. "
                "Install it with: pip install langchain-ollama"
            )
    else:
        # Use vLLM for GPU-based embeddings
        return OpenAIEmbeddings(
            model=VLLM_MODEL_NAME,
            openai_api_base=VLLM_URL,
            openai_api_key="NOT_USED"
        )