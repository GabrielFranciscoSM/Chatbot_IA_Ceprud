# api.py (servIA)
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from query_logic import (
    initialize_models,
    query_rag,
    get_base_model_response,
)
import os
import csv
from datetime import datetime
from typing import Dict, List, Tuple

app = FastAPI()

# Configuración CORS para permitir llamadas desde servWEB
origins = ["http://<IP_servWEB>:puerto"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Estructura para almacenar el historial de usuarios
user_data: Dict[str, Dict[str, object]] = {}

# Inicialización de modelos
@app.on_event("startup")
async def on_startup():
    initialize_models()

def log_user_message(email: str, message: str, subject: str, response: str, sources: List[str]):
    """
    Guarda los mensajes del usuario y las respuestas en un archivo CSV para auditoría.
    """
    os.makedirs("logs", exist_ok=True)
    path = os.path.join("logs", "chat_logs.csv")
    now = datetime.now()
    row = [email, message, now.strftime("%H:%M:%S"), now.strftime("%Y-%m-%d"), subject, ",".join(sources) or "N/A"]
    header = []
    if not os.path.exists(path):
        header = [["user", "message", "time", "date", "subject", "sources"]]
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for h in header:
            writer.writerow(h)
        writer.writerow(row)

def get_user_session(email: str, subject: str) -> List[Tuple[str, str]]:
    """
    Devuelve el historial de usuario. Si cambia la asignatura, se reinicia el historial.
    """
    data = user_data.get(email)
    if not data or data.get("subject") != subject:
        # Nueva sesión o asignatura diferente: reiniciar
        user_data[email] = {"subject": subject, "history": []}
    return user_data[email]["history"]

def update_user_history(email: str, question: str, answer: str):
    """
    Actualiza el historial del usuario.
    """
    hist: List[Tuple[str, str]] = user_data[email]["history"]
    hist.append((question, answer))
    if len(hist) > 7:  # Mantener un máximo de 7 interacciones
        hist.pop(0)

@app.post("/chat", response_model=dict)
async def chat(
    message: str = Form(...),
    subject: str = Form("default"),
    email: str = Form("anonimo"),
    mode: str = Form("rag"),
):
    """
    Endpoint para procesar consultas del chatbot.
    """
    if not message.strip():
        return {"response": "❌ Por favor, escribe una pregunta."}

    # Obtener el historial del usuario
    history = get_user_session(email, subject.lower())

    # Determinar el modo de respuesta
    if mode in ["rag", "rag_lora"]:
        result = query_rag(
            message,
            chroma_path=f"./chroma/{subject.lower()}",
            use_finetuned=(mode == "rag_lora"),
            history=history,
        )
    elif mode == "base":
        result = get_base_model_response(message, history=history)
    else:
        return {"response": "❌ Modo no válido."}

    # Procesar la respuesta
    resp: str = result['response']
    sources: List[str] = result.get('sources', [])
    used: str = result.get('model_used', '')

    clean = resp.replace('🤖: ', '')
    update_user_history(email, message, clean)
    log_user_message(email, message, subject.lower(), resp, sources)

    return {
        "response": f"🤖: {resp}",
        "sources": sources,
        "model_used": used,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)