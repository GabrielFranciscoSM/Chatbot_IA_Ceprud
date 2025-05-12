# api.py (servIA)
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
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
origins = ["http://<IP_servWEB>:8080"]  # Asegúrate de cambiar <IP_servWEB> por la IP real
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Estructura para almacenar el historial de usuarios
user_data: Dict[str, Dict] = {}

def log_user_message(email: str, message: str, subject: str, response: str, sources: List[str]):
    """
    Guarda cada interacción del usuario en un archivo CSV para auditoría.
    """
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "chat_logs.csv")
    
    now = datetime.now()
    row = [
        email,
        message,
        now.strftime("%H:%M:%S"),
        now.strftime("%Y-%m-%d"),
        subject,
        ",".join(sources) if sources else "N/A"
    ]
    
    file_exists = os.path.isfile(log_path)
    
    with open(log_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["user", "message", "time", "date", "subject", "sources"])
        writer.writerow(row)

def get_user_session(email: str, subject: str) -> List[Tuple[str, str]]:
    """
    Devuelve el historial del usuario para una asignatura específica.
    Si cambia de asignatura, reinicia el historial.
    """
    if email not in user_data:
        user_data[email] = {"subject": subject, "history": []}
    elif user_data[email]["subject"].lower() != subject.lower():
        # Reiniciar historial si cambia la asignatura
        user_data[email] = {"subject": subject, "history": []}
    
    return user_data[email]["history"]

def update_user_history(email: str, question: str, answer: str):
    """
    Agrega una nueva entrada al historial del usuario.
    Límite de historial: 5 interacciones máximas.
    """
    hist: List[Tuple[str, str]] = user_data[email]["history"]
    hist.append((question, answer))
    if len(hist) > 5:
        hist.pop(0)

@app.on_event("startup")
async def on_startup():
    """
    Carga modelos y funciones al iniciar el servidor.
    """
    print("🚀 Iniciando servidor de IA...")
    try:
        initialize_models()
        print("✅ Modelos cargados correctamente.")
    except Exception as e:
        print(f"❌ Error al cargar los modelos: {str(e)}")
        raise RuntimeError("No se pudieron cargar los modelos.")

@app.post("/chat", response_class=JSONResponse)
async def chat_endpoint(
    message: str = Form(...),
    subject: str = Form("default"),
    email: str = Form("anonimo"),
    mode: str = Form("rag")
):
    """
    Endpoint principal del chatbot.
    Recibe consultas y devuelve respuesta usando RAG, base model o fine-tuned.
    """
    # Normalizar mensaje
    user_message = message.strip()
    selected_subject = subject.lower()
    selected_mode = mode.lower()

    if not user_message:
        return JSONResponse(content={"response": "❌ Por favor, escribe una pregunta."}, status_code=400)

    # Obtener historial del usuario
    history = get_user_session(email, selected_subject)

    # Determinar qué función usar según el modo
    try:
        if selected_mode == "base":
            result = get_base_model_response(user_message, history=history)
        elif selected_mode in ["rag", "rag_lora"]:
            chroma_path = os.path.join(".", "chroma", selected_subject)
            if not os.path.exists(chroma_path):
                return JSONResponse(
                    content={"response": f"❌ No hay datos disponibles para '{selected_subject}'."},
                    status_code=404
                )
            result = query_rag(
                user_message,
                chroma_path=chroma_path,
                use_finetuned=(selected_mode == "rag_lora"),
                history=history
            )
        else:
            return JSONResponse(
                content={"response": f"❌ Modo no válido: '{mode}'"},
                status_code=400
            )

        # Procesar resultado
        clean_response = result["response"].replace("🤖: ", "")
        update_user_history(email, user_message, clean_response)
        log_user_message(email, user_message, selected_subject, result["response"], result.get("sources", []))

        print(f"💬 Mensaje: {user_message}", "Source:", result.get("sources", []), "Modelo:", result.get("model_used", selected_mode))
        if not clean_response:
            return JSONResponse(content={"response": "❌ No se encontró respuesta."}, status_code=404)

        return JSONResponse(content={
            "response": f"🤖: {clean_response}",
            "sources": result.get("sources", []),
            "model_used": result.get("model_used", selected_mode)
        })

    except Exception as e:
        print(f"⚠️ Error al procesar la solicitud: {str(e)}")
        return JSONResponse(
            content={"response": "❌ Ocurrió un error al procesar tu solicitud."},
            status_code=500
        )

@app.get("/graphs/{filename}")
async def serve_graph(filename: str):
    """
    Sirve gráficas generadas desde el directorio local.
    """
    graph_path = os.path.join(".", "graphs", filename)
    if not os.path.exists(graph_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")
    return FileResponse(graph_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)