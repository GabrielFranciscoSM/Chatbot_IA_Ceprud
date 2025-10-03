"""
User service client for communicating with the MongoDB user service.

This module provides a simple HTTP client to interact with the user service
for CRUD operations on user data.
"""

import httpx
import logging
from typing import List, Optional, Dict, Any
import os

logger = logging.getLogger(__name__)

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8083")


class UserServiceClient:
    """HTTP client for the user service"""
    
    def __init__(self, base_url: str = USER_SERVICE_URL):
        self.base_url = base_url.rstrip('/')
        self.timeout = 30.0
    
    async def create_user(self, email: str, name: str, role: str = "student") -> Optional[Dict[str, Any]]:
        """Create a new user"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/users",
                    json={
                        "email": email,
                        "name": name,
                        "role": role
                    }
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error creating user: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/users/email/{email}")
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            if e.response.status_code == 404:
                return None
            logger.error(f"HTTP error getting user by email: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/users/{user_id}")
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            if e.response.status_code == 404:
                return None
            logger.error(f"HTTP error getting user by ID: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    async def update_user(self, user_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update user data"""
        try:
            # Filter out None values
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            if not update_data:
                return None
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.put(
                    f"{self.base_url}/users/{user_id}",
                    json=update_data
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error updating user: {e}")
            return None
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return None
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all users with pagination"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/users",
                    params={"skip": skip, "limit": limit}
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error getting all users: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user by ID"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.delete(f"{self.base_url}/users/{user_id}")
                response.raise_for_status()
                return True
        except httpx.HTTPError as e:
            logger.error(f"HTTP error deleting user: {e}")
            return False
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Check if user service is healthy"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return response.json().get("status") == "healthy"
        except Exception as e:
            logger.error(f"User service health check failed: {e}")
            return False
    
    # --- Subject Management Methods ---
    
    async def get_user_subjects(self, email: str) -> Optional[Dict[str, Any]]:
        """Get all subjects for a user by email"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/users/email/{email}/subjects")
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            if e.response.status_code == 404:
                return None
            logger.error(f"HTTP error getting user subjects: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting user subjects: {e}")
            return None
    
    async def add_subject_to_user(self, email: str, subject_id: str) -> Optional[Dict[str, Any]]:
        """Add a subject to a user by email"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/users/email/{email}/subjects",
                    json={"subject_id": subject_id}
                )
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            if e.response.status_code == 404:
                return None
            if e.response.status_code == 400:
                # Subject already exists
                logger.warning(f"Subject {subject_id} already added to user {email}")
                return None
            logger.error(f"HTTP error adding subject to user: {e}")
            return None
        except Exception as e:
            logger.error(f"Error adding subject to user: {e}")
            return None
    
    async def remove_subject_from_user(self, email: str, subject_id: str) -> Optional[Dict[str, Any]]:
        """Remove a subject from a user by email"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.delete(
                    f"{self.base_url}/users/email/{email}/subjects/{subject_id}"
                )
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            if e.response.status_code == 404:
                return None
            logger.error(f"HTTP error removing subject from user: {e}")
            return None
        except Exception as e:
            logger.error(f"Error removing subject from user: {e}")
            return None


# Global client instance
user_service = UserServiceClient()
