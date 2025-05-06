import os
import csv
from datetime import datetime
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from query_logic import (
    initialize_models,
    BASE_MODEL,
    TOKENIZER,
    EMBEDDING_FUNCTION,
    load_finetuned_model,
    generate_response,
    query_rag,
    get_base_model_response,
)
from langchain_chroma import Chroma

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

# Montar directorios estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/graphs", StaticFiles(directory="graphs"), name="graphs")

# Configuración de plantillas
templates = Jinja2Templates(directory="templates")

# Configuración de Chroma
BASE_CHROMA_PATH = "./chroma"

# Historial de chat por usuario
chat_histories = {}
MAX_HISTORY_LENGTH = 5

# Inicializar modelos y embeddings
@app.on_event("startup")
async def on_startup():
    initialize_models()


def log_user_message(email: str, message: str, subject: str, response: str, sources: list):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "chat_logs.csv")
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    file_exists = os.path.isfile(log_file)
    sources_str = ",".join(sources) if sources else "N/A"

    with open(log_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["user", "message", "time", "date", "subject", "sources"])
        writer.writerow([email, message, time, date, subject, sources_str])


def get_user_history(email: str):
    return chat_histories.setdefault(email, [])


def update_user_history(email: str, question: str, answer: str):
    history = chat_histories.setdefault(email, [])
    history.append((question, answer))
    if len(history) > MAX_HISTORY_LENGTH:
        history.pop(0)


def build_prompt_with_history(user_message: str, history: list, context_text: str = None) -> str:
    prompt = (
        "RESPONDE A LAS SIGUIENTES PREGUNTAS CON EL CONTEXTO PROPORCIONADO, "
        "ERES UN BOT DE LA UGR EXPERTO EN LA MATERIA:\n\n"
    )
    if context_text:
        prompt += f"{context_text}\n\n"
    if history:
        prompt += "HISTORIAL DE CONVERSACIÓN RECIENTE:\n"
        for q, a in history:
            prompt += f"Usuario: {q}\nBot: {a}\n\n"
    prompt += f"LA PREGUNTA ACTUAL A RESPONDER ES:\n{user_message}\n\n### RESPUESTA:"
    return prompt

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('index.html', {"request": request})

@app.get("/graphs", response_class=JSONResponse)
async def list_graphs():
    graphs_dir = "graphs"
    if not os.path.exists(graphs_dir):
        return []
    specific_graphs = ["calendar.png", "hours.png", "subjects.png", "users.png"]
    return [f for f in os.listdir(graphs_dir) if f in specific_graphs]

@app.get("/graphs/{filename}")
async def serve_graph(filename: str):
    file_path = os.path.join("graphs", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@app.post("/chat", response_class=JSONResponse)
async def chat(
    message: str = Form(...),
    subject: str = Form('default'),
    email: str = Form('anonimo'),
    mode: str = Form('rag')
):
    user_message = message.strip()
    selected_subject = subject.lower()
    user_email = email
    selected_mode = mode.lower()

    if not user_message:
        return {"response": "❌ Por favor, escribe una pregunta."}

    user_history = get_user_history(user_email)
    chroma_path = os.path.join(BASE_CHROMA_PATH, selected_subject)

    if selected_mode != 'base' and not os.path.exists(chroma_path):
        return {"response": f"❌ No hay datos disponibles para la asignatura '{selected_subject}'."}

    try:
        if selected_mode in ['rag', 'rag_lora']:
            result = query_rag(
                user_message,
                chroma_path,
                subject=selected_subject,
                use_finetuned=(selected_mode=='rag_lora'),
                history=user_history
            )
            response_text = result['response']
            sources = result['sources']
            used = result['model_used']
        elif selected_mode == 'base':
            result = get_base_model_response(user_message, history=user_history)
            response_text = result['response']
            sources = []
            used = result['model_used']
        else:
            return {"response": "❌ Modo no válido."}

        clean_response = response_text.replace('🤖: ', '')
        update_user_history(user_email, user_message, clean_response)
        log_user_message(user_email, user_message, selected_subject, response_text, sources)

        return {
            "response": f"🤖: {response_text}",
            "sources": sources,
            "model_used": used
        }
    except Exception as e:
        print(f"Error durante el procesamiento: {e}")
        return {"response": "❌ Ocurrió un error al procesar tu solicitud."}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5001)
