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
    UserCreateRequest, UserCreateResponse, UserLoginRequest, UserLoginResponse,
    UserLogoutResponse, UserProfileResponse, UserProfileUpdateRequest, UserProfileUpdateResponse,
    check_rate_limit, get_rate_limit_info, 
    RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW,
    BASE_LOG_DIR, API_VERSION
)
from domain.query_logic import (
    query_rag, clear_session
)
from services import (
    get_or_create_session, update_session_activity, cleanup_old_sessions,
    log_request_info, classify_query_type, estimate_query_complexity, anonymize_user_id,
    active_sessions
)
from services.logging_service import log_user_message, log_session_event, log_learning_event, log_conversation_message
from services.user_service import user_service
import logging

# Get logger 
logger = logging.getLogger(__name__)

# Create a router object instead of a FastAPI app
router = APIRouter()

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
    
    return RateLimitStatus(
        requests_made=rate_info['requests_made'],
        requests_remaining=rate_info['requests_remaining'],
        reset_time=rate_info['reset_time'],
        user_identifier=user_identifier
    )

@router.get("/rate-limit-info", response_model=RateLimitStatus)
async def get_rate_limit_info_endpoint(email: str):
    """
    Check rate limit status for a specific user email (frontend compatible endpoint).
    Query parameter version of the rate limit check.
    """
    user_identifier = anonymize_user_id(email)
    rate_info = get_rate_limit_info(user_identifier)
    
    return RateLimitStatus(
        requests_made=rate_info['requests_made'],
        requests_remaining=rate_info['requests_remaining'],
        reset_time=rate_info['reset_time'],
        user_identifier=user_identifier
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


# --- User Management Endpoints ---

@router.post("/user/create", response_model=UserCreateResponse, responses={
    400: {"model": ErrorResponse}, 
    500: {"model": ErrorResponse}
})
async def create_user_endpoint(
    request: Request,
    user_request: UserCreateRequest
):
    """
    Create a new user account
    """
    start_time = time.time()
    
    try:
        # Check if user service is available
        if not await user_service.health_check():
            log_request_info(request, start_time, 503)
            raise HTTPException(
                status_code=503,
                detail="User service is not available"
            )
        
        # Check if user already exists
        existing_user = await user_service.get_user_by_email(user_request.email)
        if existing_user:
            log_request_info(request, start_time, 400)
            return UserCreateResponse(
                success=False,
                message="User with this email already exists"
            )
        
        # Create new user
        new_user = await user_service.create_user(
            email=user_request.email,
            name=user_request.name,
            role=user_request.role
        )
        
        if new_user:
            log_request_info(request, start_time, 201)
            logger.info(f"User created successfully: {user_request.email}")
            
            return UserCreateResponse(
                success=True,
                user_id=new_user["id"],
                message="User created successfully"
            )
        else:
            log_request_info(request, start_time, 500)
            return UserCreateResponse(
                success=False,
                message="Failed to create user"
            )
            
    except Exception as e:
        error_msg = f"Error creating user: {str(e)}"
        logger.error(error_msg)
        log_request_info(request, start_time, 500)
        
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )


@router.post("/user/login", response_model=UserLoginResponse, responses={
    400: {"model": ErrorResponse}, 
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def login_user_endpoint(
    request: Request,
    login_request: UserLoginRequest
):
    """
    Login user (simple email-based authentication)
    """
    start_time = time.time()
    
    try:
        # Check if user service is available
        if not await user_service.health_check():
            log_request_info(request, start_time, 503)
            raise HTTPException(
                status_code=503,
                detail="User service is not available"
            )
        
        # Find user by email
        user = await user_service.get_user_by_email(login_request.email)
        
        if not user:
            log_request_info(request, start_time, 404)
            return UserLoginResponse(
                success=False,
                message="User not found"
            )
        
        if not user.get("active", True):
            log_request_info(request, start_time, 400)
            return UserLoginResponse(
                success=False,
                message="User account is inactive"
            )
        
        log_request_info(request, start_time, 200)
        logger.info(f"User logged in: {login_request.email}")
        
        return UserLoginResponse(
            success=True,
            user_id=user["id"],
            name=user["name"],
            role=user["role"],
            message="Login successful"
        )
            
    except Exception as e:
        error_msg = f"Error during login: {str(e)}"
        logger.error(error_msg)
        log_request_info(request, start_time, 500)
        
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )


@router.post("/user/logout", response_model=UserLogoutResponse, responses={
    500: {"model": ErrorResponse}
})
async def logout_user_endpoint(
    request: Request
):
    """
    Logout user (simple endpoint for consistency)
    """
    start_time = time.time()
    
    log_request_info(request, start_time, 200)
    
    return UserLogoutResponse(
        success=True,
        message="Logout successful"
    )


@router.get("/user/profile", response_model=UserProfileResponse, responses={
    400: {"model": ErrorResponse},
    404: {"model": ErrorResponse}, 
    500: {"model": ErrorResponse}
})
async def get_user_profile_endpoint(
    request: Request,
    email: str
):
    """
    Get user profile by email
    """
    start_time = time.time()
    
    try:
        # Check if user service is available
        if not await user_service.health_check():
            log_request_info(request, start_time, 503)
            raise HTTPException(
                status_code=503,
                detail="User service is not available"
            )
        
        user = await user_service.get_user_by_email(email)
        
        if not user:
            log_request_info(request, start_time, 404)
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        log_request_info(request, start_time, 200)
        
        return UserProfileResponse(
            user_id=user["id"],
            email=user["email"],
            name=user["name"],
            role=user["role"],
            active=user["active"],
            created_at=user["created_at"]
        )
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error getting user profile: {str(e)}"
        logger.error(error_msg)
        log_request_info(request, start_time, 500)
        
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )


@router.put("/user/profile", response_model=UserProfileUpdateResponse, responses={
    400: {"model": ErrorResponse},
    404: {"model": ErrorResponse}, 
    500: {"model": ErrorResponse}
})
async def update_user_profile_endpoint(
    request: Request,
    email: str,
    profile_request: UserProfileUpdateRequest
):
    """
    Update user profile
    """
    start_time = time.time()
    
    try:
        # Check if user service is available
        if not await user_service.health_check():
            log_request_info(request, start_time, 503)
            raise HTTPException(
                status_code=503,
                detail="User service is not available"
            )
        
        # First get the user to get their ID
        user = await user_service.get_user_by_email(email)
        
        if not user:
            log_request_info(request, start_time, 404)
            return UserProfileUpdateResponse(
                success=False,
                message="User not found"
            )
        
        # Update user
        updated_user = await user_service.update_user(
            user_id=user["id"],
            name=profile_request.name,
            role=profile_request.role
        )
        
        if updated_user:
            log_request_info(request, start_time, 200)
            logger.info(f"User profile updated: {email}")
            
            user_profile = UserProfileResponse(
                user_id=updated_user["id"],
                email=updated_user["email"],
                name=updated_user["name"],
                role=updated_user["role"],
                active=updated_user["active"],
                created_at=updated_user["created_at"]
            )
            
            return UserProfileUpdateResponse(
                success=True,
                message="Profile updated successfully",
                user=user_profile
            )
        else:
            log_request_info(request, start_time, 500)
            return UserProfileUpdateResponse(
                success=False,
                message="Failed to update profile"
            )
            
    except Exception as e:
        error_msg = f"Error updating user profile: {str(e)}"
        logger.error(error_msg)
        log_request_info(request, start_time, 500)
        
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )

