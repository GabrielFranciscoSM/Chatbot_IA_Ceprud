"""
Subject management endpoints for the CEPRUD chatbot.

This module handles:
- Listing user's enrolled subjects
- Adding subjects to users
- Removing subjects from users
"""

import time
import logging
from fastapi import APIRouter, HTTPException, Request

from core import (
    AddSubjectRequest,
    RemoveSubjectRequest,
    UserSubjectsResponse,
    ErrorResponse
)
from services import log_request_info
from services.user_service import user_service

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["subjects"])


@router.get("/user/subjects", response_model=UserSubjectsResponse, responses={
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def get_user_subjects_endpoint(
    request: Request,
    email: str
):
    """
    Get all subjects for a user by email.
    
    Returns a list of all subjects (course IDs) that the user is enrolled in
    or has access to. Used for subject selection in the frontend.
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
        
        # Get user subjects
        subjects_data = await user_service.get_user_subjects(email)
        
        if subjects_data is None:
            log_request_info(request, start_time, 404)
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        log_request_info(request, start_time, 200)
        return UserSubjectsResponse(
            success=True,
            subjects=subjects_data.get("subjects", []),
            message="Subjects retrieved successfully"
        )
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error getting user subjects: {str(e)}"
        logger.error(error_msg)
        log_request_info(request, start_time, 500)
        
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )


@router.post("/user/subjects", response_model=UserSubjectsResponse, responses={
    400: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def add_subject_to_user_endpoint(
    request: Request,
    subject_request: AddSubjectRequest
):
    """
    Add a subject to a user's list of subjects.
    
    Enrolls a user in a new subject/course. The user must exist,
    and the subject will be added to their subjects list.
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
        
        # Add subject to user
        result = await user_service.add_subject_to_user(
            email=subject_request.email,
            subject_id=subject_request.subject_id
        )
        
        if result is None:
            log_request_info(request, start_time, 404)
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        log_request_info(request, start_time, 200)
        logger.info(f"Added subject {subject_request.subject_id} to user {subject_request.email}")
        
        return UserSubjectsResponse(
            success=True,
            subjects=result.get("subjects", []),
            message=f"Subject {subject_request.subject_id} added successfully"
        )
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error adding subject to user: {str(e)}"
        logger.error(error_msg)
        log_request_info(request, start_time, 500)
        
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )


@router.delete("/user/subjects/{subject_id}", response_model=UserSubjectsResponse, responses={
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def remove_subject_from_user_endpoint(
    request: Request,
    subject_id: str,
    email: str
):
    """
    Remove a subject from a user's list of subjects.
    
    Unenrolls a user from a subject/course. The user and subject must exist.
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
        
        # Remove subject from user
        result = await user_service.remove_subject_from_user(
            email=email,
            subject_id=subject_id
        )
        
        if result is None:
            log_request_info(request, start_time, 404)
            raise HTTPException(
                status_code=404,
                detail="User or subject not found"
            )
        
        log_request_info(request, start_time, 200)
        logger.info(f"Removed subject {subject_id} from user {email}")
        
        return UserSubjectsResponse(
            success=True,
            subjects=result.get("subjects", []),
            message=f"Subject {subject_id} removed successfully"
        )
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error removing subject from user: {str(e)}"
        logger.error(error_msg)
        log_request_info(request, start_time, 500)
        
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )
