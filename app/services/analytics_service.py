"""
Analytics and logging service.

This module handles:
- Learning analytics logging
- Request logging and performance tracking
- User interaction logging
- Educational event tracking
"""

import os
import csv
import time
from datetime import datetime
from typing import List, Optional
from fastapi import Request
import logging

from core.config import BASE_LOG_DIR

logger = logging.getLogger(__name__)


def log_session_event(session_id: str, user_id: str, subject: str, event_type: str):
    """
    Log session-related events for learning analytics.
    
    Args:
        session_id: Session identifier
        user_id: Anonymized user identifier  
        subject: Subject/course name
        event_type: Type of session event
    """
    log_path = os.path.join(BASE_LOG_DIR, "learning_sessions.csv")
    file_exists = os.path.exists(log_path)
    
    # Create log entry
    now = datetime.now()
    row = [
        session_id,
        user_id,
        subject,
        event_type,
        now.strftime("%Y-%m-%d"),
        now.strftime("%H:%M:%S"),
        now.timestamp()
    ]
    
    # Write to CSV
    with open(log_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "session_id", "user_id", "subject", "event_type", 
                "date", "time", "timestamp"
            ])
        writer.writerow(row)


def log_request_info(request: Request, start_time: float, status_code: int, response_size: int = 0):
    """
    Log request information for performance monitoring.
    
    Args:
        request: FastAPI request object
        start_time: Request start timestamp
        status_code: HTTP response status code
        response_size: Size of response in bytes
    """
    duration = time.time() - start_time
    
    logger.info(
        f"Request: {request.method} {request.url.path} | "
        f"Status: {status_code} | "
        f"Duration: {duration:.3f}s | "
        f"Size: {response_size} bytes"
    )


def log_user_message(email: str, message: str, subject: str, response: str, sources: List[str], 
                    session_id: str, query_type: str, complexity: str, model_used: str):
    """
    Log comprehensive user interaction data for enhanced learning analytics.
    
    Args:
        email: User email (will be anonymized)
        message: User's message
        subject: Subject/course
        response: Bot's response  
        sources: Source documents used
        session_id: Session identifier
        query_type: Classified query type
        complexity: Estimated query complexity
        model_used: Model used for response
    """
    log_path = os.path.join(BASE_LOG_DIR, "chat_interactions_enhanced.csv")
    file_exists = os.path.exists(log_path)
    
    # Create enhanced log entry
    now = datetime.now()
    row = [
        session_id,
        email[:8] + "...",  # Partial anonymization for debugging
        subject,
        len(message),  # Message length instead of full message for privacy
        query_type,
        complexity,
        len(response),  # Response length
        len(sources),  # Number of sources
        model_used,
        now.strftime("%Y-%m-%d"),
        now.strftime("%H:%M:%S"),
        now.timestamp()
    ]
    
    # Write to CSV
    with open(log_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "session_id", "user_id_partial", "subject", "message_length", 
                "query_type", "complexity", "response_length", "source_count",
                "model_used", "date", "time", "timestamp"
            ])
        writer.writerow(row)


def log_learning_event(session_id: str, event_type: str, topic: str, confidence_level: Optional[str] = None):
    """
    Log learning-related events for educational analytics.
    
    Args:
        session_id: Session identifier
        event_type: Type of learning event
        topic: Topic or subject matter
        confidence_level: Confidence level if applicable
    """
    log_path = os.path.join(BASE_LOG_DIR, "learning_events.csv")
    file_exists = os.path.exists(log_path)
    
    # Create learning event entry
    now = datetime.now()
    row = [
        session_id,
        event_type,
        topic,
        confidence_level or "N/A",
        now.strftime("%Y-%m-%d"),
        now.strftime("%H:%M:%S"),
        now.timestamp()
    ]
    
    # Write to CSV
    with open(log_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "session_id", "event_type", "topic", "confidence_level", 
                "date", "time", "timestamp"
            ])
        writer.writerow(row)


def classify_query_type(query: str) -> str:
    """
    Simple query classification for analytics.
    
    Args:
        query: User's query text
        
    Returns:
        Query type classification
    """
    query_lower = query.lower()
    
    # Question patterns
    question_words = ['qué', 'cómo', 'cuándo', 'dónde', 'por qué', 'quién', 'cuál']
    if any(word in query_lower for word in question_words) or '?' in query:
        return "question"
    
    # Definition requests
    definition_words = ['define', 'definir', 'concepto', 'significado', 'qué es']
    if any(word in query_lower for word in definition_words):
        return "definition"
    
    # Example requests
    example_words = ['ejemplo', 'ejemplos', 'caso', 'casos', 'muestra', 'ilustra']
    if any(word in query_lower for word in example_words):
        return "example"
    
    # Problem solving
    problem_words = ['problema', 'resolver', 'solución', 'cálculo', 'calcular', 'ejercicio']
    if any(word in query_lower for word in problem_words):
        return "problem_solving"
    
    # Comparison requests
    comparison_words = ['diferencia', 'comparar', 'versus', 'vs', 'mejor', 'peor']
    if any(word in query_lower for word in comparison_words):
        return "comparison"
    
    return "general"


def estimate_query_complexity(query: str) -> str:
    """
    Estimate query complexity for analytics.
    
    Args:
        query: User's query text
        
    Returns:
        Complexity level (simple, medium, complex)
    """
    # Simple heuristics for complexity estimation
    word_count = len(query.split())
    
    # Complex indicators
    complex_words = [
        'análisis', 'evaluar', 'comparar', 'contrastar', 'justificar', 
        'argumentar', 'demostrar', 'optimizar', 'integrar', 'sintetizar'
    ]
    
    # Medium complexity indicators  
    medium_words = [
        'explicar', 'describir', 'identificar', 'clasificar', 'aplicar',
        'resolver', 'calcular', 'determinar', 'establecer'
    ]
    
    query_lower = query.lower()
    
    if word_count > 20 or any(word in query_lower for word in complex_words):
        return "complex"
    elif word_count > 10 or any(word in query_lower for word in medium_words):
        return "medium"
    else:
        return "simple"
