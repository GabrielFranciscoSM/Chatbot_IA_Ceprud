"""
Pydantic models for request/response validation and API documentation.

This module contains all data models used by the API endpoints for:
- Request validation
- Response formatting 
- OpenAPI documentation generation
- Error handling
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator


class ChatRequest(BaseModel):
    """Simple request model for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=1000, description="User query text")
    subject: str = Field(default="default", max_length=50, description="Subject/course name")
    email: str = Field(default="anonimo", max_length=100, description="User email (anonymized)")
    mode: str = Field(default="rag", description="Chat mode (rag, base, rag_lora)")
    
    @field_validator('mode')
    def validate_mode(cls, v):
        allowed_modes = ['rag', 'base', 'rag_lora']
        if v.lower() not in allowed_modes:
            raise ValueError(f'Mode must be one of: {allowed_modes}')
        return v.lower()
    
    @field_validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()


class ChatResponse(BaseModel):
    """Simple response model for chat endpoint"""
    response: str = Field(..., description="Bot response text")
    sources: List[str] = Field(default=[], description="Source documents used")
    model_used: str = Field(..., description="Model type used for response")
    session_id: str = Field(..., description="Session identifier")
    query_type: str = Field(..., description="Classified query type")


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")


class RateLimitResponse(BaseModel):
    """Rate limit exceeded response"""
    error: str = Field(..., description="Rate limit error message")
    requests_made: int = Field(..., description="Number of requests made in current window")
    requests_remaining: int = Field(..., description="Requests remaining in current window")
    reset_time: int = Field(..., description="Unix timestamp when rate limit resets")
    retry_after: int = Field(..., description="Seconds to wait before retrying")


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(default="1.0.0", description="API version")


class RateLimitStatus(BaseModel):
    """Rate limit status information"""
    requests_made: int = Field(..., description="Number of requests made in current window")
    requests_remaining: int = Field(..., description="Requests remaining in current window")
    reset_time: int = Field(..., description="Unix timestamp when rate limit resets")
    user_identifier: str = Field(..., description="User identifier (anonymized)")


class ClearSessionRequest(BaseModel):
    """Request model for clearing a chat session"""
    subject: str = Field(..., max_length=50, description="Subject/course name")
    email: str = Field(..., max_length=100, description="User email")


class ClearSessionResponse(BaseModel):
    """Response model for clearing a chat session"""
    success: bool = Field(..., description="Whether the session was cleared successfully")
    message: str = Field(..., description="Confirmation message")
    session_id: str = Field(..., description="ID of the cleared session")
