"""
LTI User Service

Handles user creation and authentication from LTI launches.
Integrates with existing MongoDB user service.
"""

import logging
from typing import Dict, Optional
import sys
import os

# Add parent directory to path to import services
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.user_service import user_service

logger = logging.getLogger(__name__)


class LTIUserService:
    """
    Service for managing users from LTI launches.
    """
    
    def __init__(self):
        self.user_service = user_service
    
    async def create_or_update_user(
        self,
        lti_user_id: str,
        email: str,
        name: str,
        given_name: str = "",
        family_name: str = ""
    ) -> Dict:
        """
        Create or update user from LTI launch data.
        
        Args:
            lti_user_id: LTI user ID from platform
            email: User email
            name: User full name
            given_name: User first name
            family_name: User last name
            
        Returns:
            User dictionary from MongoDB
        """
        # Use email as the primary identifier, fallback to lti_user_id
        user_email = email if email else f"lti_{lti_user_id}@moodle.local"
        user_name = name if name else f"{given_name} {family_name}".strip() or f"LTI User {lti_user_id}"
        
        # Try to find user by email first
        user = None
        if user_email:
            try:
                user = await self.user_service.get_user_by_email(user_email)
                logger.info(f"Found existing user by email: {user_email}")
            except Exception as e:
                logger.debug(f"User not found by email: {e}")
        
        # If user doesn't exist, create new user
        if not user:
            logger.info(f"Creating new user from LTI: {user_email}")
            try:
                user = await self.user_service.create_user(
                    email=user_email,
                    name=user_name,
                    role="student"  # Default role, can be enhanced with LTI roles
                )
                logger.info(f"Created user: {user.get('_id')}")
            except Exception as e:
                logger.error(f"Failed to create user: {e}")
                raise ValueError(f"Cannot create user: {e}")
        
        return user
