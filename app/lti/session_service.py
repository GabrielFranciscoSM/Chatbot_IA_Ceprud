"""
LTI Session Service

Manages LTI sessions with MongoDB persistence.
"""

import logging
import uuid
import secrets
from typing import Dict, Optional
from datetime import datetime, timedelta
from .database import get_database

logger = logging.getLogger(__name__)


class LTISessionService:
    """
    Service for managing LTI sessions with MongoDB.
    """
    
    def __init__(self):
        self.db = get_database()
        self.sessions_collection = self.db["lti_sessions"]
    
    async def create_or_get_session(
        self,
        user_id: str,
        lti_user_id: str,
        context_id: str,
        context_label: str,
        subject: str
    ) -> Dict:
        """
        Create a new session or retrieve existing one for user+context.
        
        Args:
            user_id: MongoDB user ID
            lti_user_id: LTI user ID
            context_id: Moodle course/context ID
            context_label: Course label
            subject: Mapped subject name
            
        Returns:
            Session dictionary
        """
        # Try to find existing active session for this user+context
        existing_session = await self.sessions_collection.find_one({
            "user_id": user_id,
            "context_id": context_id,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if existing_session:
            logger.info(f"Found existing session for user {user_id} in context {context_id}")
            # Update last activity AND subject (in case mapping changed)
            await self.sessions_collection.update_one(
                {"_id": existing_session["_id"]},
                {"$set": {
                    "last_activity": datetime.utcnow(),
                    "subject": subject,  # Update subject in case mapping changed
                    "context_label": context_label  # Also update context_label
                }}
            )
            # Update the returned session object with new values
            existing_session["subject"] = subject
            existing_session["context_label"] = context_label
            existing_session["last_activity"] = datetime.utcnow()
            return existing_session
        
        # Create new session
        session_token = secrets.token_urlsafe(32)
        session = {
            "session_token": session_token,
            "user_id": user_id,
            "lti_user_id": lti_user_id,
            "context_id": context_id,
            "context_label": context_label,
            "subject": subject,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=8)  # 8 hour session
        }
        
        result = await self.sessions_collection.insert_one(session)
        session["_id"] = result.inserted_id
        
        logger.info(f"Created new session {session_token} for user {user_id}")
        return session
    
    async def get_session(self, session_token: str) -> Optional[Dict]:
        """
        Get session by token.
        
        Args:
            session_token: Session token
            
        Returns:
            Session dictionary or None
        """
        session = await self.sessions_collection.find_one({
            "session_token": session_token,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if session:
            # Update last activity
            await self.sessions_collection.update_one(
                {"_id": session["_id"]},
                {"$set": {"last_activity": datetime.utcnow()}}
            )
        
        return session
    
    async def delete_session(self, session_token: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_token: Session token
            
        Returns:
            True if deleted, False otherwise
        """
        result = await self.sessions_collection.delete_one({"session_token": session_token})
        return result.deleted_count > 0
    
    async def cleanup_expired_sessions(self):
        """
        Remove expired sessions from database.
        """
        result = await self.sessions_collection.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        logger.info(f"Cleaned up {result.deleted_count} expired sessions")
