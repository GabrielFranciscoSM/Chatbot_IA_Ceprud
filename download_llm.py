import argparse
import os
from huggingface_hub import snapshot_download
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

RECOMMENDED_MODELS = [
    os.getenv("MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0"),
    "mistralai/Mistral-7B-v0.1",
    "deepseek-ai/deepseek-llm-7b-chat",
    "BAAI/bge-m3",
    "TheBloke/TinyLlama-1.1B-Chat-v1.0-AWQ",
    "jinaai/jina-embeddings-v2-base-es",
    "jinaai/jina-embeddings-v3",
    "Qwen/Qwen3-Embedding-0.6B",
    "casperhansen/llama-3-8b-instruct-awq",
    "Sreenington/Phi-3-mini-4k-instruct-AWQ"
]

def download_model(model_name, target_dir):
    print(f"Descargando el modelo '{model_name}' en '{target_dir}'...")
    snapshot_download(
        repo_id=model_name,
        local_dir=target_dir,
        local_dir_use_symlinks=False,
        resume_download=True
    )
    print("Descarga completada.")

def mostrar_menu():
    print("Selecciona el modelo a descargar:")
    for idx, model in enumerate(RECOMMENDED_MODELS, 1):
        print(f"{idx}. {model}")
    print(f"{len(RECOMMENDED_MODELS)+1}. Salir")
    opcion = input("Introduce el número de la opción: ")
    return opcion

def main():
    while True:
        opcion = mostrar_menu()
        if not opcion.isdigit():
            print("Por favor, introduce un número válido.")
            continue
        opcion = int(opcion)
        if opcion == len(RECOMMENDED_MODELS) + 1:
            print("Saliendo...")
            break
        elif 1 <= opcion <= len(RECOMMENDED_MODELS):
            model_name = RECOMMENDED_MODELS[opcion - 1]
            model_dir = os.path.join("models", model_name.replace("/", "--"))
            os.makedirs(model_dir, exist_ok=True)
            download_model(model_name, model_dir)
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
