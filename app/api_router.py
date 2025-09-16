import os
import csv
import time
import uuid
import hashlib
from datetime import datetime
from fastapi import APIRouter, Form, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
from core import (
    ChatRequest, ChatResponse, ErrorResponse, 
    RateLimitResponse, HealthResponse, RateLimitStatus,
    ClearSessionRequest, ClearSessionResponse,
    check_rate_limit, get_rate_limit_info, 
    RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW,
    BASE_LOG_DIR, API_VERSION
)
from domain.query_logic import (
    query_rag, clear_session
)
from services import (
    get_or_create_session, update_session_activity, cleanup_old_sessions,
    log_session_event, log_request_info, log_user_message, log_learning_event,
    classify_query_type, estimate_query_complexity, anonymize_user_id,
    active_sessions
)
import logging

# Get logger (configuration is handled by config module)
logger = logging.getLogger(__name__)

# Create a router object instead of a FastAPI app
router = APIRouter()

# This dictionary will store user session data (legacy - will be refactored)
user_data: Dict[str, Dict[str, object]] = {}

# --- API Endpoints ---
@router.post("/chat", response_model=ChatResponse, responses={
    400: {"model": ErrorResponse}, 
    429: {"model": RateLimitResponse}, 
    500: {"model": ErrorResponse}
})
async def chat_endpoint(
    request: Request,
    chat_request: ChatRequest
):
    """
    Main chatbot endpoint with Pydantic validation and rate limiting. 
    Handles queries and returns responses using RAG, base model, or fine-tuned models.
    
    Rate limit: 20 requests per minute per user.
    """
    start_time = time.time()
    
    # Extract validated data from Pydantic model
    user_message = chat_request.message
    selected_subject = chat_request.subject.lower()
    selected_mode = chat_request.mode.lower()
    email = chat_request.email

    # Create user identifier for rate limiting (use anonymized user ID)
    user_identifier = anonymize_user_id(email)
    
    # Check rate limit before processing
    if not check_rate_limit(user_identifier):
        rate_info = get_rate_limit_info(user_identifier)
        current_time = int(time.time())
        retry_after = max(1, rate_info['reset_time'] - current_time)
        
        log_request_info(request, start_time, 429)
        
        # Return rate limit error with helpful information
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "requests_made": rate_info['requests_made'],
                "requests_remaining": rate_info['requests_remaining'],
                "reset_time": rate_info['reset_time'],
                "retry_after": retry_after
            }
        )

    # Get or create session for this user-subject combination
    session_id = get_or_create_session(email, selected_subject)
    
    # Periodic cleanup of old sessions (every request, but lightweight)
    if len(active_sessions) > 10:  # Only cleanup when we have many sessions
        cleanup_old_sessions()

    logger.info(f"Chat request received - Session: {session_id}, Subject: {selected_subject}, Mode: {selected_mode}, Email: {email}")

    try:
        query_start_time = time.time()
        
        if selected_mode == 'base':
            result = query_rag(user_message, subject=selected_subject, use_finetuned=False, email=email)
        elif selected_mode in ['rag', 'rag_lora']:
            result = query_rag(
                user_message,
                subject=selected_subject,
                use_finetuned=(selected_mode == 'rag_lora'),
                email=email
                )
        else:
            log_request_info(request, start_time, 400)
            raise HTTPException(status_code=400, detail=f"❌ Modo no válido: '{selected_mode}'")

        query_end_time = time.time()
        response_time_ms = int((query_end_time - query_start_time) * 1000)

        response_text = result.get('response', '')
        sources = result.get('sources', [])
        model_used = result.get('model_used', '')

        # Enhanced logging with learning analytics
        query_type = classify_query_type(user_message)
        complexity = estimate_query_complexity(user_message)
        
        log_user_message(
            email=email, 
            message=user_message, 
            subject=selected_subject, 
            response=response_text, 
            sources=sources,
            session_id=session_id,
            query_type=query_type,
            complexity=complexity,
            model_used=model_used
        )

        response_size = len(response_text.encode('utf-8')) + sum(len(src.encode('utf-8')) for src in sources)
        log_request_info(request, start_time, 200, response_size)

        # Get rate limit info for response headers
        rate_info = get_rate_limit_info(user_identifier)

        # Create response with rate limit headers
        response_data = ChatResponse(
            response=f"🤖: {response_text}",
            sources=sources,
            model_used=model_used,
            session_id=session_id,
            query_type=query_type
        )
        
        # Return JSON response with rate limit headers
        response = JSONResponse(
            content=response_data.dict(),
            headers={
                "X-RateLimit-Limit": str(RATE_LIMIT_REQUESTS),
                "X-RateLimit-Remaining": str(rate_info['requests_remaining']),
                "X-RateLimit-Reset": str(rate_info['reset_time'])
            }
        )
        return response

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        log_request_info(request, start_time, 500)
        raise HTTPException(status_code=500, detail="❌ An error occurred while processing your request.")

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Simple health check endpoint to verify API is running and Pydantic models work.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version=API_VERSION
    )

@router.get("/rate-limit/{email}", response_model=RateLimitStatus)
async def get_rate_limit_status(email: str):
    """
    Check rate limit status for a specific user email.
    Useful for frontend applications to show remaining requests.
    """
    user_identifier = anonymize_user_id(email)
    rate_info = get_rate_limit_info(user_identifier)
    current_time = int(time.time())
    retry_after = max(0, rate_info['reset_time'] - current_time)
    
    return RateLimitStatus(
        requests_made=rate_info['requests_made'],
        requests_remaining=rate_info['requests_remaining'],
        reset_time=rate_info['reset_time'],
        user_identifier=user_identifier[:8] + "..."  # Show only first 8 chars for privacy
    )

@router.get("/rate-limit-info", response_model=RateLimitStatus)
async def get_rate_limit_info_endpoint(email: str):
    """
    Check rate limit status for a specific user email (frontend compatible endpoint).
    Query parameter version of the rate limit check.
    """
    user_identifier = anonymize_user_id(email)
    rate_info = get_rate_limit_info(user_identifier)
    current_time = int(time.time())
    retry_after = max(0, rate_info['reset_time'] - current_time)
    
    return RateLimitStatus(
        requests_made=rate_info['requests_made'],
        requests_remaining=rate_info['requests_remaining'],
        reset_time=rate_info['reset_time'],
        user_identifier=user_identifier[:8] + "..."  # Show only first 8 chars for privacy
    )

@router.post("/clear-session", response_model=ClearSessionResponse, responses={
    400: {"model": ErrorResponse}, 
    429: {"model": RateLimitResponse}, 
    500: {"model": ErrorResponse}
})
async def clear_session_endpoint(
    request: Request,
    clear_request: ClearSessionRequest
):
    """
    Clear the conversation memory for a specific user-subject combination.
    This removes all chat history and resets the context for the specified session.
    """
    start_time = time.time()
    
    # Extract validated data from Pydantic model
    subject = clear_request.subject.lower()
    email = clear_request.email
    
    # Create user identifier for rate limiting (same as chat endpoint)
    user_identifier = anonymize_user_id(email)
    
    # Check rate limit (lighter limit for clear operations)
    if not check_rate_limit(user_identifier):
        rate_info = get_rate_limit_info(user_identifier)
        current_time = int(time.time())
        retry_after = max(1, rate_info['reset_time'] - current_time)
        
        log_request_info(request, start_time, 429)
        
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "requests_made": rate_info['requests_made'], 
                "requests_remaining": rate_info['requests_remaining'],
                "reset_time": rate_info['reset_time'],
                "retry_after": retry_after
            }
        )
    
    logger.info(f"Clear session request - Subject: {subject}, Email: {email}")
    
    try:
        # Clear the session memory
        success = clear_session(subject, email)
        
        if success:
            # Also update our session tracking
            session_id = get_or_create_session(email, subject)
            
            # Log the session clear event
            log_session_event(
                session_id=session_id,
                user_id=user_identifier,  # Use anonymized user ID
                subject=subject,
                event_type="session_cleared"
            )
            
            log_request_info(request, start_time, 200)
            
            return ClearSessionResponse(
                success=True,
                message=f"Session cleared successfully for {subject}",
                session_id=session_id
            )
        else:
            log_request_info(request, start_time, 500)
            raise HTTPException(
                status_code=500,
                detail="Failed to clear session memory"
            )
            
    except Exception as e:
        error_msg = f"Error clearing session: {str(e)}"
        logger.error(error_msg)
        log_request_info(request, start_time, 500)
        
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )

