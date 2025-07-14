# vllm_server_tester.py

import requests
import json

# Define the base endpoints for your vLLM servers
ENDPOINT_MODEL_BASE = "http://localhost:8000/v1"
ENDPOINT_MODEL_EMBEDDINGS = "http://localhost:8001/v1"

# Define the model paths
PATH_MODEL_BASE = "/models/TinyLlama--TinyLlama-1.1B-Chat-v1.0"
PATH_MODEL_EMBEDDINGS = "/models/BAAI--bge-m3"

def call_completions(prompt: str = "¿Qué es la inteligencia artificial?"):
    """
    Calls the /completions endpoint and returns the response object.
    """
    try:
        response = requests.post(
            f"{ENDPOINT_MODEL_BASE}/completions",
            headers={"Content-Type": "application/json"},
            json={
                "model": PATH_MODEL_BASE,
                "prompt": prompt,
                "max_tokens": 128,
            }
        )
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during /completions request: {e}")
        return None

def call_chat_completions(prompt: str = "¿Cuál es la capital de Francia?"):
    """
    Calls the /chat/completions endpoint and returns the response object.
    """
    try:
        response = requests.post(
            f"{ENDPOINT_MODEL_BASE}/chat/completions",
            headers={"Content-Type": "application/json"},
            json={
                "model": PATH_MODEL_BASE,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 128
            }
        )
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during /chat/completions request: {e}")
        return None
def call_streaming_completions(prompt: str = "Escribe un poema corto sobre la programación."):
    """
    Calls the /completions endpoint with streaming enabled and returns the response object.
    """
    try:
        response = requests.post(
            f"{ENDPOINT_MODEL_BASE}/completions",
            headers={"Content-Type": "application/json"},
            json={
                "model": PATH_MODEL_BASE,
                "prompt": prompt,
                "max_tokens": 128,
                "stream": True
            },
            stream=True  # This is crucial for streaming
        )
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during streaming /completions request: {e}")
        return None
    
def call_embeddings(input_text: str = "¿Qué es la inteligencia artificial?"):
    """
    Calls the /embeddings endpoint and returns the response object.
    """
    try:
        response = requests.post(
            f"{ENDPOINT_MODEL_EMBEDDINGS}/embeddings",
            headers={"Content-Type": "application/json"},
            json={
                "model": PATH_MODEL_EMBEDDINGS,
                "input": input_text
            }
        )
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during /embeddings request: {e}")
        return None

if __name__ == '__main__':
    # You can still run this file directly to manually inspect outputs
    print("--- Manual Test for /completions ---")
    completion_response = call_completions()
    if completion_response:
        print(json.dumps(completion_response.json(), indent=2))

    print("\n--- Manual Test for /chat/completions ---")
    chat_response = call_chat_completions()
    if chat_response:
        print(json.dumps(chat_response.json(), indent=2))

    print("\n--- Manual Test for /embeddings ---")
    embedding_response = call_embeddings()
    if embedding_response:
        print(json.dumps(embedding_response.json(), indent=2))