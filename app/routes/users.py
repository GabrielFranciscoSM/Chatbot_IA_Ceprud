"""
User management endpoints for the CEPRUD chatbot.

This module handles:
- User registration and account creation
- User login (email-based authentication)
- User logout
- User profile retrieval and updates
"""

import time
import logging
from fastapi import APIRouter, HTTPException, Request

from core import (
    UserCreateRequest,
    UserCreateResponse,
    UserLoginRequest,
    UserLoginResponse,
    UserLogoutResponse,
    UserProfileResponse,
    UserProfileUpdateRequest,
    UserProfileUpdateResponse,
    ErrorResponse
)
from services import log_request_info
from services.user_service import user_service

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["users"])


@router.post("/user/create", response_model=UserCreateResponse, responses={
    400: {"model": ErrorResponse}, 
    500: {"model": ErrorResponse}
})
async def create_user_endpoint(
    request: Request,
    user_request: UserCreateRequest
):
    """
    Create a new user account.
    
    Validates that the user doesn't already exist and creates a new user
    with the provided email, name, and role.
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
    Login user with email-based authentication.
    
    Validates user exists and is active, returning user details on success.
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
    Logout user.
    
    Simple endpoint for consistency. In a stateless API, this primarily
    serves to signal logout intent to the client.
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
    Get user profile by email.
    
    Returns complete user profile including personal information,
    role, active status, and enrolled subjects.
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
            created_at=user["created_at"],
            subjects=user.get("subjects", [])
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
    Update user profile.
    
    Allows updating user name and role. Email cannot be changed.
    Returns updated user profile on success.
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
                created_at=updated_user["created_at"],
                subjects=updated_user.get("subjects", [])
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
