"""
Chat endpoints for the CEPRUD chatbot.

This module handles:
- Main chat conversations with RAG-enhanced responses
- Session management and conversation memory clearing
- Rate limiting and usage tracking
- Conversation logging and analytics
"""

import time
from typing import Dict
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from core import (
    ChatRequest,
    ChatResponse,
    ClearSessionRequest,
    ClearSessionResponse,
    RateLimitResponse,
    ErrorResponse,
    check_rate_limit,
    get_rate_limit_info,
    RATE_LIMIT_REQUESTS
)
from domain.query_logic import (
    query_rag,
    clear_session
)
from services import (
    get_or_create_session,
    cleanup_old_sessions,
    log_request_info,
    anonymize_user_id,
    classify_query_type,
    estimate_query_complexity,
    active_sessions
)
from services.logging_service import (
    log_conversation_message,
    log_user_message,
    log_learning_event,
    log_session_event
)

# Setup logging
import logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["chat"])


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
    Process a chat message and return an AI-generated response.
    
    This endpoint:
    1. Validates and rate-limits the request
    2. Queries the RAG system for context-aware answers
    3. Logs conversation data for analytics
    4. Returns the response with metadata
    
    Rate limiting is applied per anonymized user to prevent abuse.
    Sessions are automatically created/retrieved for conversation continuity.
    """
    start_time = time.time()
    
    # Extract validated data from Pydantic model
    user_message = chat_request.message
    selected_subject = chat_request.subject.lower()
    email = chat_request.email
    mode = chat_request.mode
    
    # Create anonymized user identifier for rate limiting
    user_identifier = anonymize_user_id(email)
    
    # Check rate limit before processing
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
    
    logger.info(f"Chat request - Subject: {selected_subject}, Email: {email}, Question: {user_message[:100]}...")
    
    try:
        # Get or create session for this user-subject combination
        session_id = get_or_create_session(email, selected_subject)
        
        # Periodic cleanup of old sessions (every request, but lightweight)
        if len(active_sessions) > 10:  # Only cleanup when we have many sessions
            cleanup_old_sessions()
        
        # Query the RAG system
        result = query_rag(user_message, subject=selected_subject, use_finetuned=False, email=email)
        
        response_text = result.get('response', '')
        sources = result.get('sources', [])
        model_used = result.get('model_used', '')

        query_type = classify_query_type(user_message)
        complexity = estimate_query_complexity(user_message)
        
        conversation_timestamp = time.time()
        
        # Log user message
        await log_conversation_message(
            session_id=session_id,
            user_id=user_identifier,
            subject=selected_subject,
            message_type="user",
            message_content=user_message,
            timestamp=conversation_timestamp
        )
        
        # Log bot response
        await log_conversation_message(
            session_id=session_id,
            user_id=user_identifier,
            subject=selected_subject,
            message_type="bot",
            message_content=response_text,
            timestamp=conversation_timestamp + 0.001  # Slightly later timestamp
        )
        
        await log_user_message(
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

        # Log learning events for educational analytics
        if query_type == "question" and complexity in ["medium", "complex"]:
            await log_learning_event(
                session_id=session_id,
                event_type="complex_question_asked",
                topic=selected_subject,
                confidence_level="medium" if len(sources) > 0 else "low"
            )
        elif query_type == "concept" or "concepto" in user_message.lower():
            await log_learning_event(
                session_id=session_id,
                event_type="concept_inquiry",
                topic=selected_subject,
                confidence_level="high" if len(sources) > 2 else "medium"
            )

        response_size = len(response_text.encode('utf-8')) + sum(len(src.encode('utf-8')) for src in sources)
        log_request_info(request, start_time, 200, response_size)

        # Get rate limit info for response headers
        rate_info = get_rate_limit_info(user_identifier)

        response_data = ChatResponse(
            response=f"🤖: {response_text}",
            sources=sources,
            model_used=model_used,
            session_id=session_id,
            query_type=query_type
        )
        
        # Return JSON response with rate limit headers
        response = JSONResponse(
            content=response_data.model_dump(),
            headers={
                "X-RateLimit-Limit": str(RATE_LIMIT_REQUESTS),
                "X-RateLimit-Remaining": str(rate_info['requests_remaining']),
                "X-RateLimit-Reset": str(rate_info['reset_time'])
            }
        )
        return response
        
    except Exception as e:
        error_msg = f"Error processing chat request: {str(e)}"
        logger.error(error_msg, exc_info=True)
        log_request_info(request, start_time, 500)
        
        raise HTTPException(
            status_code=500,
            detail="❌ An error occurred while processing your request."
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
    Useful when users want to start a fresh conversation or switch topics.
    
    Rate limiting is applied (lighter than chat endpoint) to prevent abuse.
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
            await log_session_event(
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
