"""
LTI 1.3 Data Models

Defines the data structures for LTI platform configurations and sessions.
"""

from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class LTIPlatformConfig(BaseModel):
    """
    Configuration for an LTI platform (e.g., Moodle instance).
    Stored in MongoDB for each Moodle installation that uses this tool.
    """
    platform_id: str = Field(..., description="Unique identifier for the platform (issuer URL)")
    client_id: str = Field(..., description="OAuth 2.0 client ID issued by the platform")
    auth_login_url: str = Field(..., description="Platform's OIDC authentication URL")
    auth_token_url: str = Field(..., description="Platform's OAuth 2.0 token URL")
    auth_audience: Optional[str] = Field(None, description="Token audience (optional)")
    key_set_url: str = Field(..., description="Platform's public keyset URL (JWKS)")
    deployment_ids: List[str] = Field(default_factory=list, description="Allowed deployment IDs")
    
    # Tool configuration
    tool_private_key: Optional[str] = Field(None, description="Tool's private RSA key (PEM format)")
    tool_public_jwk: Optional[Dict] = Field(None, description="Tool's public key as JWK")
    
    # Metadata
    platform_name: str = Field(default="Moodle", description="Human-readable platform name")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    active: bool = Field(default=True, description="Whether this platform config is active")
    
    class Config:
        json_schema_extra = {
            "example": {
                "platform_id": "https://moodle.example.com",
                "client_id": "GBx1F4LefiUr7bZ",
                "auth_login_url": "https://moodle.example.com/mod/lti/auth.php",
                "auth_token_url": "https://moodle.example.com/mod/lti/token.php",
                "key_set_url": "https://moodle.example.com/mod/lti/certs.php",
                "deployment_ids": ["1"],
                "platform_name": "UGR Moodle"
            }
        }


class LTISession(BaseModel):
    """
    Represents an LTI launch session.
    Links Moodle user/course to chatbot session.
    """
    session_id: str = Field(..., description="Unique session identifier")
    
    # LTI Identity
    lti_user_id: str = Field(..., description="LTI user ID from platform")
    lti_deployment_id: str = Field(..., description="LTI deployment ID")
    platform_id: str = Field(..., description="Platform issuer")
    
    # User mapping
    chatbot_user_id: Optional[str] = Field(None, description="Mapped chatbot user ID")
    email: Optional[str] = Field(None, description="User email from LTI claims")
    name: Optional[str] = Field(None, description="User name from LTI claims")
    roles: List[str] = Field(default_factory=list, description="LTI roles")
    
    # Context (course) mapping
    context_id: Optional[str] = Field(None, description="LTI context ID (course)")
    context_label: Optional[str] = Field(None, description="Course short name")
    context_title: Optional[str] = Field(None, description="Course full name")
    mapped_subject: Optional[str] = Field(None, description="Chatbot subject ID mapped from course")
    
    # Session metadata
    launch_id: str = Field(..., description="Unique launch identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Session expiration")
    
    # Additional data
    resource_link_id: Optional[str] = Field(None, description="LTI resource link ID")
    custom_params: Dict = Field(default_factory=dict, description="Custom LTI parameters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "lti_session_abc123",
                "lti_user_id": "user123",
                "lti_deployment_id": "1",
                "platform_id": "https://moodle.example.com",
                "email": "student@correo.ugr.es",
                "name": "Juan Pérez",
                "roles": ["Learner"],
                "context_id": "course_456",
                "context_label": "IS-2025",
                "context_title": "Ingeniería de Servidores 2025",
                "mapped_subject": "ingenieria_de_servidores",
                "launch_id": "launch_xyz789"
            }
        }


class LTILaunchRequest(BaseModel):
    """Request model for LTI launch validation"""
    id_token: str = Field(..., description="LTI JWT token")
    state: str = Field(..., description="OIDC state parameter")


class LTILaunchResponse(BaseModel):
    """Response after successful LTI launch"""
    success: bool
    session_id: str
    redirect_url: str
    user_id: Optional[str] = None
    subject: Optional[str] = None
    message: Optional[str] = None
