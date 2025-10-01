from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., min_length=1, max_length=100, description="User full name")
    role: str = Field(default="student", description="User role (student, teacher, admin)")
    active: bool = Field(default=True, description="Whether user is active")
    subjects: List[str] = Field(default_factory=list, description="List of subject IDs associated with user")


class UserCreate(UserBase):
    """Model for creating a new user"""
    pass


class UserUpdate(BaseModel):
    """Model for updating user data"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[str] = None
    active: Optional[bool] = None
    subjects: Optional[List[str]] = None


class User(UserBase):
    """Complete user model with ID and timestamps"""
    id: str = Field(..., description="User ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class AddSubjectRequest(BaseModel):
    """Model for adding a subject to a user"""
    subject_id: str = Field(..., min_length=1, description="Subject ID to add")


class RemoveSubjectRequest(BaseModel):
    """Model for removing a subject from a user"""
    subject_id: str = Field(..., min_length=1, description="Subject ID to remove")


class SubjectsResponse(BaseModel):
    """Model for returning user's subjects"""
    subjects: List[str] = Field(..., description="List of subject IDs")
