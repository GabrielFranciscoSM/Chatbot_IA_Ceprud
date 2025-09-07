import os
import csv
from datetime import datetime
from fastapi import APIRouter, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, List#, Tuple
from logic.query_logic import (
    query_rag
)
from dotenv import load_dotenv

# Create a router object instead of a FastAPI app
router = APIRouter()

load_dotenv()
# --- Configuration and Shared State ---
BASE_CHROMA_PATH = os.getenv("BASE_CHROMA_PATH", "chroma")
BASE_LOG_DIR = os.getenv("BASE_LOG_DIR", "logs")

# This dictionary will store user session data
user_data: Dict[str, Dict[str, object]] = {}

# --- Helper Functions (Shared Logic) ---
def log_user_message(email: str, message: str, subject: str, response: str, sources: List[str]):
    """
    Saves each user interaction to a CSV file for auditing.
    """
    os.makedirs(BASE_LOG_DIR, exist_ok=True)
    log_path = os.path.join(BASE_LOG_DIR, "chat_logs.csv")
    
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

# def get_user_session(email: str, subject: str) -> List[Tuple[str, str]]:
#     """
#     Returns the user's history for a specific subject.
#     If the subject changes, the history is reset.
#     """
#     data = user_data.get(email)
#     if not data or data.get("subject") != subject:
#         user_data[email] = {"subject": subject, "history": []}
#     return user_data[email]["history"]

# --- API Endpoints ---
@router.post("/chat", response_class=JSONResponse)
async def chat_endpoint(
    message: str = Form(...),
    subject: str = Form("default"),
    email: str = Form("anonimo"),
    mode: str = Form("rag")
):
    """
    Main chatbot endpoint. Handles queries and returns responses
    using RAG, base model, or fine-tuned models.
    """
    user_message = message.strip()
    selected_subject = subject.lower()
    selected_mode = mode.lower()

    if not user_message:
        return JSONResponse(content={"response": "❌ Por favor, escribe una pregunta."}, status_code=400)

    try:
        if selected_mode == 'base':
            result = query_rag(user_message,subject=selected_subject,use_finetuned=False)
        elif selected_mode in ['rag', 'rag_lora']:
            result = query_rag(
                user_message,
                subject=selected_subject,
                use_finetuned=(selected_mode == 'rag_lora')
                )
        else:
            return JSONResponse(content={"response": f"❌ Modo no válido: '{mode}'"}, status_code=400)

        response_text = result.get('response', '')
        sources = result.get('sources', [])
        model_used = result.get('model_used', '')

        # Add interaction to history and log it
        log_user_message(email, user_message, selected_subject, response_text, sources)

        return JSONResponse(content={
            "response": f"🤖: {response_text}",
            "sources": sources,
            "model_used": model_used
        })

    except Exception as e:
        print(f"⚠️ Error processing request: {str(e)}")
        return JSONResponse(
            content={"response": "❌ An error occurred while processing your request."},
            status_code=500
        )