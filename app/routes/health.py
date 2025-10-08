"""
Health and Monitoring Routes

Provides health check and rate limit monitoring endpoints.
"""

from datetime import datetime
from fastapi import APIRouter
from core import (
    HealthResponse,
    RateLimitStatus,
    ErrorResponse,
    get_rate_limit_info,
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_WINDOW,
    API_VERSION
)
from services import anonymize_user_id

router = APIRouter(
    prefix="",
    tags=["health"]
)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Simple health check endpoint to verify API is running and Pydantic models work.
    
    Returns:
        HealthResponse: Status, timestamp, and API version
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
    
    Args:
        email: User email address
        
    Returns:
        RateLimitStatus: Current rate limit information for the user
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
    
    Args:
        email: User email address (query parameter)
        
    Returns:
        RateLimitStatus: Current rate limit information for the user
    """
    user_identifier = anonymize_user_id(email)
    rate_info = get_rate_limit_info(user_identifier)
    
    return RateLimitStatus(
        requests_made=rate_info['requests_made'],
        requests_remaining=rate_info['requests_remaining'],
        reset_time=rate_info['reset_time'],
        user_identifier=user_identifier
    )
