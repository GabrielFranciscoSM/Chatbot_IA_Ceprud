import os
import csv
from datetime import datetime
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Dict, List, Tuple

from query_logic import (
    query_rag
)

# Configuración de FastAPI
app = FastAPI()

origins = ["http://150.214.205.61:8080"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Directorios estáticos y templates
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/graphs", StaticFiles(directory="graphs"), name="graphs")
templates = Jinja2Templates(directory="templates")

# Configuración
BASE_CHROMA_PATH = "chroma"

# Estructura: email -> {'subject': str, 'history': List[(pregunta, respuesta)]}
user_data: Dict[str, Dict[str, object]] = {}

# Inicialización de modelos en arranque
declare_user_data = None

def log_user_message(email: str, message: str, subject: str, response: str, sources: List[str]):
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


#############################################################################
##################--REVISAR ES MÉTODO CON NUEVO HISTORIAL--##################
#############################################################################
def get_user_session(email: str, subject: str) -> List[Tuple[str, str]]:
    """
    Devuelve el historial de usuario. Si cambia la asignatura, se reinicia el historial.
    """
    data = user_data.get(email)
    if not data or data.get("subject") != subject:
        # nueva sesión o asignatura diferente: reiniciar
        user_data[email] = {"subject": subject, "history": []}
    return user_data[email]["history"]  # type: ignore


@app.post("/chat", response_class=JSONResponse)
async def chat(
    message: str = Form(...),
    subject: str = Form('default'),
    email: str = Form('anonimo'),
    mode: str = Form('rag')
):
    user_message = message.strip()
    sub = subject.lower()
    mode = mode.lower()

    if not user_message:
        return {"response": "❌ Por favor, escribe una pregunta."}

    chroma_path = os.path.join(BASE_CHROMA_PATH, sub)
    
    if mode != 'base' and not os.path.isdir(chroma_path):
        return {"response": f"❌ No hay datos para '{sub}'. Directorios disponibles: {os.listdir(BASE_CHROMA_PATH)}"}

    if mode in ['rag', 'rag_lora']:
        result = query_rag(
            user_message,
            chroma_path,
            subject=sub,
            use_finetuned=(mode == 'rag_lora'),
        )
    elif mode == 'base':
        result = query_rag(user_message,use_RAG=False)
    else:
        return {"response": "❌ Modo no válido."}

    resp: str = result['response']
    sources: List[str] = result.get('sources', [])
    used: str = result.get('model_used', '')

    log_user_message(email, user_message, sub, resp, sources)

    return {"response": f"🤖: {resp}", "sources": sources, "model_used": used}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('index.html', {"request": request})


@app.get("/graphs", response_class=JSONResponse)
async def list_graphs():
    d = os.path.join(os.path.dirname(__file__), "graphs")
    return [f for f in os.listdir(d) if f in ["calendar.png", "hours.png", "subjects.png", "users.png"]]


@app.get("/graphs/{fname}")
async def serve_graph(fname: str):
    p = os.path.join(os.path.dirname(__file__), "graphs", fname)
    if not os.path.exists(p):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(p)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5001)
