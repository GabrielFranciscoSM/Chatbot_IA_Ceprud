from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., min_length=1, max_length=100, description="User full name")
    role: str = Field(default="student", description="User role (student, teacher, admin)")
    active: bool = Field(default=True, description="Whether user is active")


class UserCreate(UserBase):
    """Model for creating a new user"""
    pass


class UserUpdate(BaseModel):
    """Model for updating user data"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[str] = None
    active: Optional[bool] = None


class User(UserBase):
    """Complete user model with ID and timestamps"""
    id: str = Field(..., description="User ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True
