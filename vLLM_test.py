import requests

response = requests.post(
    "http://localhost:8000/v1/completions",
    headers={"Content-Type": "application/json"},
    json={
        "model": "./models/TinyLlama--TinyLlama-1.1B-Chat-v1.0",
        "prompt": "¿Qué es la inteligencia artificial?",
        "max_tokens": 128
    }
)
print(response.json())