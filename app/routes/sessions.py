"""
Session Management Routes

Handles LTI session validation and authentication.
"""

import time
import logging
from fastapi import APIRouter, HTTPException, Request, Header
from fastapi.responses import JSONResponse
from core import ErrorResponse
from services import log_request_info
from services.user_service import user_service
from lti.session_service import LTISessionService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/session",
    tags=["sessions"]
)


@router.get("/validate", responses={
    401: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def validate_lti_session(
    request: Request,
    x_session_token: str = Header(None, alias="X-Session-Token")
):
    """
    Validate LTI session token and return user information.
    Used by frontend to authenticate users launched from Moodle.
    
    Args:
        x_session_token: Session token from LTI launch (header)
        
    Returns:
        JSON with user data, subject, and session info
        
    Raises:
        HTTPException: 401 if token invalid/missing, 500 on error
    """
    start_time = time.time()
    
    if not x_session_token:
        log_request_info(request, start_time, 401)
        raise HTTPException(
            status_code=401,
            detail="No session token provided"
        )
    
    try:
        # Initialize LTI session service
        session_service = LTISessionService()
        
        # Get session from MongoDB
        session = await session_service.get_session(x_session_token)
        
        if not session:
            log_request_info(request, start_time, 401)
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired session token"
            )
        
        # Get user information
        user_id = session.get("user_id")
        if not user_id:
            log_request_info(request, start_time, 500)
            raise HTTPException(
                status_code=500,
                detail="Session missing user information"
            )
        
        # Fetch user from user service
        user = await user_service.get_user_by_id(user_id)
        
        if not user:
            log_request_info(request, start_time, 404)
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        log_request_info(request, start_time, 200)
        logger.info(f"Session validated successfully: {x_session_token[:20]}... for user {user.get('email')}")
        
        # Handle both '_id' (MongoDB) and 'id' (user-service API response)
        user_id = user.get("_id") or user.get("id")
        
        return JSONResponse(
            content={
                "user": {
                    "id": str(user_id) if user_id else None,
                    "name": user.get("name"),
                    "email": user.get("email"),
                    "role": user.get("role", "student")
                },
                "subject": session.get("subject"),
                "context_label": session.get("context_label"),
                "lti_user_id": session.get("lti_user_id"),
                "expires_at": session.get("expires_at").isoformat() if session.get("expires_at") else None
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error validating session: {str(e)}"
        logger.error(error_msg, exc_info=True)
        log_request_info(request, start_time, 500)
        
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )
