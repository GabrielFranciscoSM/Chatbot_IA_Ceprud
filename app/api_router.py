import os
import csv
import logging
import time
import uuid
import hashlib
from datetime import datetime
from fastapi import APIRouter, Form, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
from logic.query_logic import (
    query_rag
)
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create a router object instead of a FastAPI app
router = APIRouter()

load_dotenv()
# --- Configuration and Shared State ---
BASE_CHROMA_PATH = os.getenv("BASE_CHROMA_PATH", "chroma")
BASE_LOG_DIR = os.getenv("BASE_LOG_DIR", "logs")

# Ensure logs directory exists
os.makedirs(BASE_LOG_DIR, exist_ok=True)

# Session management for learning analytics
active_sessions: Dict[str, Dict] = {}

# This dictionary will store user session data
user_data: Dict[str, Dict[str, object]] = {}

# --- Learning Analytics Helper Functions ---
def anonymize_user_id(email: str) -> str:
    """
    Create an anonymous but consistent user ID from email.
    """
    return hashlib.sha256(email.encode()).hexdigest()[:16]

def classify_query_type(query: str) -> str:
    """
    Classify the type of question being asked.
    """
    query_lower = query.lower()
    
    # Definition questions
    if any(word in query_lower for word in ['qué es', 'define', 'concepto', 'significado']):
        return 'definition'
    
    # Procedural questions
    if any(word in query_lower for word in ['cómo', 'pasos', 'proceso', 'método']):
        return 'procedure'
    
    # Comparison questions
    if any(word in query_lower for word in ['diferencia', 'comparar', 'vs', 'versus']):
        return 'comparison'
    
    # Example questions
    if any(word in query_lower for word in ['ejemplo', 'muestra', 'caso']):
        return 'example'
    
    # Clarification questions
    if any(word in query_lower for word in ['explica', 'aclarar', 'entender']):
        return 'clarification'
    
    return 'general'

def estimate_query_complexity(query: str) -> str:
    """
    Estimate query complexity based on length and keywords.
    """
    word_count = len(query.split())
    
    complex_indicators = ['porque', 'relación', 'impacto', 'análisis', 'evaluar']
    has_complex_terms = any(term in query.lower() for term in complex_indicators)
    
    if word_count > 15 or has_complex_terms:
        return 'high'
    elif word_count > 8:
        return 'medium'
    else:
        return 'low'

def get_or_create_session(user_email: str, subject: str) -> str:
    """
    Get existing session or create new one for user-subject combination.
    """
    user_id = anonymize_user_id(user_email)
    session_key = f"{user_id}_{subject}"
    
    # Check for existing active session (within last 30 minutes)
    current_time = time.time()
    
    if session_key in active_sessions:
        last_activity = active_sessions[session_key]['last_activity']
        if current_time - last_activity < 1800:  # 30 minutes
            active_sessions[session_key]['last_activity'] = current_time
            return active_sessions[session_key]['session_id']
    
    # Create new session
    session_id = str(uuid.uuid4())[:8]
    active_sessions[session_key] = {
        'session_id': session_id,
        'user_id': user_id,
        'subject': subject,
        'start_time': current_time,
        'last_activity': current_time,
        'message_count': 0
    }
    
    # Log session start
    log_session_event(session_id, user_id, subject, 'session_start')
    
    return session_id

def log_session_event(session_id: str, user_id: str, subject: str, event_type: str):
    """
    Log session-level events (start, end, etc.)
    """
    log_path = os.path.join(BASE_LOG_DIR, "learning_sessions.csv")
    
    now = datetime.now()
    row = [
        session_id,
        user_id,
        subject,
        event_type,
        now.strftime("%Y-%m-%d"),
        now.strftime("%H:%M:%S"),
        int(time.time())
    ]
    
    file_exists = os.path.isfile(log_path)
    
    with open(log_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "session_id", "user_id", "subject", "event_type", 
                "date", "time", "timestamp"
            ])
        writer.writerow(row)

# --- Helper Functions (Shared Logic) ---
def log_request_info(request: Request, start_time: float, status_code: int, response_size: int = 0):
    """
    Log detailed request information for monitoring and debugging.
    """
    duration = time.time() - start_time
    logger.info(
        f"Request: {request.method} {request.url.path} | "
        f"Status: {status_code} | "
        f"Duration: {duration:.3f}s | "
        f"Response Size: {response_size}b | "
        f"Client IP: {request.client.host if request.client else 'unknown'}"
    )

# --- Helper Functions (Shared Logic) ---
def log_user_message(email: str, message: str, subject: str, response: str, sources: List[str], 
                    response_time_ms: Optional[int] = None, session_id: Optional[str] = None):
    """
    Enhanced logging function that saves interaction data for learning analytics.
    """
    # Get or create session
    if not session_id:
        session_id = get_or_create_session(email, subject)
    
    # Update session activity
    user_id = anonymize_user_id(email)
    session_key = f"{user_id}_{subject}"
    if session_key in active_sessions:
        active_sessions[session_key]['message_count'] += 1
    
    # Classify and analyze the query
    query_type = classify_query_type(message)
    query_complexity = estimate_query_complexity(message)
    
    # Calculate metrics
    query_length = len(message.split())
    response_length = len(response.split())
    source_count = len(sources) if sources else 0
    
    # Log to enhanced interactions file
    log_path = os.path.join(BASE_LOG_DIR, "chat_interactions_enhanced.csv")
    
    now = datetime.now()
    row = [
        session_id,
        user_id,
        message,
        response,
        now.strftime("%H:%M:%S"),
        now.strftime("%Y-%m-%d"),
        subject,
        ",".join(sources) if sources else "N/A",
        query_type,
        query_complexity,
        query_length,
        response_length,
        source_count,
        response_time_ms or 0,
        int(time.time())
    ]
    
    file_exists = os.path.isfile(log_path)
    
    with open(log_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "session_id", "user_id", "query", "response", "time", "date", 
                "subject", "sources", "query_type", "query_complexity", 
                "query_length", "response_length", "source_count", 
                "response_time_ms", "timestamp"
            ])
        writer.writerow(row)

def log_learning_event(session_id: str, event_type: str, topic: str, confidence_level: Optional[str] = None):
    """
    Log specific learning events for educational analytics.
    """
    log_path = os.path.join(BASE_LOG_DIR, "learning_events.csv")
    
    now = datetime.now()
    row = [
        session_id,
        event_type,
        topic,
        confidence_level or "unknown",
        now.strftime("%Y-%m-%d"),
        now.strftime("%H:%M:%S"),
        int(time.time())
    ]
    
    file_exists = os.path.isfile(log_path)
    
    with open(log_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "session_id", "event_type", "topic", "confidence_level", 
                "date", "time", "timestamp"
            ])
        writer.writerow(row)

# --- API Endpoints ---
@router.post("/chat", response_class=JSONResponse)
async def chat_endpoint(
    request: Request,
    message: str = Form(...),
    subject: str = Form("default"),
    email: str = Form("anonimo"),
    mode: str = Form("rag")
):
    """
    Main chatbot endpoint. Handles queries and returns responses
    using RAG, base model, or fine-tuned models.
    """
    start_time = time.time()
    user_message = message.strip()
    selected_subject = subject.lower()
    selected_mode = mode.lower()

    # Get or create session for this user-subject combination
    session_id = get_or_create_session(email, selected_subject)
    
    # Periodic cleanup of old sessions (every request, but lightweight)
    if len(active_sessions) > 10:  # Only cleanup when we have many sessions
        cleanup_old_sessions()

    logger.info(f"Chat request received - Session: {session_id}, Subject: {selected_subject}, Mode: {selected_mode}, Email: {email}")

    if not user_message:
        log_request_info(request, start_time, 400)
        return JSONResponse(content={"response": "❌ Por favor, escribe una pregunta."}, status_code=400)

    try:
        query_start_time = time.time()
        
        if selected_mode == 'base':
            result = query_rag(user_message,subject=selected_subject,use_finetuned=False)
        elif selected_mode in ['rag', 'rag_lora']:
            result = query_rag(
                user_message,
                subject=selected_subject,
                use_finetuned=(selected_mode == 'rag_lora')
                )
        else:
            log_request_info(request, start_time, 400)
            return JSONResponse(content={"response": f"❌ Modo no válido: '{mode}'"}, status_code=400)

        query_end_time = time.time()
        response_time_ms = int((query_end_time - query_start_time) * 1000)

        response_text = result.get('response', '')
        sources = result.get('sources', [])
        model_used = result.get('model_used', '')

        # Enhanced logging with learning analytics
        log_user_message(
            email=email, 
            message=user_message, 
            subject=selected_subject, 
            response=response_text, 
            sources=sources,
            response_time_ms=response_time_ms,
            session_id=session_id
        )
        
        # Log learning event
        query_type = classify_query_type(user_message)
        log_learning_event(session_id, f"query_{query_type}", selected_subject)

        response_size = len(response_text.encode('utf-8')) + sum(len(src.encode('utf-8')) for src in sources)
        log_request_info(request, start_time, 200, response_size)

        return JSONResponse(content={
            "response": f"🤖: {response_text}",
            "sources": sources,
            "model_used": model_used,
            "session_id": session_id,  # Include session ID for frontend tracking
            "query_type": query_type   # Include query classification
        })

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        log_request_info(request, start_time, 500)
        return JSONResponse(
            content={"response": "❌ An error occurred while processing your request."},
            status_code=500
        )

def cleanup_old_sessions():
    """
    Clean up old sessions to prevent memory leaks.
    Remove sessions older than 1 hour.
    """
    current_time = time.time()
    sessions_to_remove = []
    
    for session_key, session_data in active_sessions.items():
        if current_time - session_data['last_activity'] > 3600:  # 1 hour
            sessions_to_remove.append(session_key)
            # Log session end
            log_session_event(
                session_data['session_id'], 
                session_data['user_id'], 
                session_data['subject'], 
                'session_timeout'
            )
    
    for session_key in sessions_to_remove:
        del active_sessions[session_key]
    
    if sessions_to_remove:
        logger.info(f"Cleaned up {len(sessions_to_remove)} expired sessions")