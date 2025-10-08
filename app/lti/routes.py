"""
LTI 1.3 FastAPI Endpoints

Implements OIDC login, launch, and JWKS endpoints for Moodle integration.
"""

from fastapi import APIRouter, Request, Response, HTTPException, Form
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from .config import LTIConfig
from .jwt_validator import LTIJWTValidator
from .user_service import LTIUserService
from .session_service import LTISessionService
import os
import logging
import jwt
from urllib.parse import urlencode
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Enable debug logging

# Load config
config_dir = os.getenv("LTI_CONFIG_DIR", "./lti_config")
lti_config = LTIConfig(config_dir)

# Initialize services
jwt_validator = LTIJWTValidator(
    platform_id=os.getenv("MOODLE_ISSUER", "https://moodle.ugr.es"),
    client_id=os.getenv("MOODLE_CLIENT_ID", "GBx1F4LefiUr7bZ"),
    jwks_url=os.getenv("MOODLE_JWKS_URL", "https://moodle.ugr.es/mod/lti/certs.php")
)
user_service = LTIUserService()
session_service = LTISessionService()

# Course to subject mapping (can be moved to a config/database later)
# Maps Moodle course labels to frontend subject IDs
COURSE_SUBJECT_MAPPING = {
    # Moodle course label -> Frontend subject ID
    "IS": "ingenieria_de_servidores",
    "MAC": "modelos_avanzados_computacion",
    "META": "metaheuristicas",
    "IE1": "inferencia_estadistica_1",
    "EST": "estadistica",
}

@router.get("/lti/jwks", response_class=JSONResponse)
def jwks():
    """JWKS endpoint for Moodle to fetch public keys"""
    jwks = lti_config.get_jwks()
    return jwks

@router.get("/lti/login")
@router.post("/lti/login")
async def lti_login(request: Request):
    """OIDC login initiation endpoint (redirects to Moodle) - Accepts both GET and POST"""
    # Extract parameters from either query params (GET) or form data (POST)
    if request.method == "POST":
        form_data = await request.form()
        params_dict = dict(form_data)
    else:
        params_dict = dict(request.query_params)
    
    logger.info(f"LTI Login - Received parameters: {params_dict}")
    
    # Extract required parameters from Moodle
    iss = params_dict.get("iss")  # Platform issuer
    login_hint = params_dict.get("login_hint")
    target_link_uri = params_dict.get("target_link_uri")
    lti_message_hint = params_dict.get("lti_message_hint", "")
    client_id = params_dict.get("client_id") or os.getenv("MOODLE_CLIENT_ID", "GBx1F4LefiUr7bZ")
    
    # Validate required parameters (temporarily disabled for debugging)
    if not login_hint:
        logger.warning(f"Missing login_hint parameter. Received params: {params_dict}")
        # Use a dummy value for now to see the full flow
        login_hint = "debug-user"
    
    # Get the authentication URL - usually iss + /mod/lti/auth.php for Moodle
    if iss:
        auth_login_url = f"{iss}/mod/lti/auth.php"
    else:
        auth_login_url = os.getenv("MOODLE_AUTH_LOGIN_URL", "https://testchatbot.moodlecloud.com/mod/lti/auth.php")
    
    # If target_link_uri not provided, use our launch endpoint
    if not target_link_uri:
        base_url = os.getenv('CHATBOT_BASE_URL', 'http://localhost:8080')
        target_link_uri = f"{base_url}/api/lti/launch"
    
    # Generate random state and nonce
    import secrets
    state = secrets.token_urlsafe(16)
    nonce = secrets.token_urlsafe(16)
    
    # Build OIDC authentication request
    oidc_params = {
        "scope": "openid",
        "response_type": "id_token",
        "response_mode": "form_post",  # Tell Moodle to POST the id_token back
        "client_id": client_id,
        "redirect_uri": target_link_uri,
        "login_hint": login_hint,
        "state": state,
        "nonce": nonce,
        "prompt": "none"
    }
    
    if lti_message_hint:
        oidc_params["lti_message_hint"] = lti_message_hint
    
    oidc_url = f"{auth_login_url}?{urlencode(oidc_params)}"
    logger.info(f"LTI Login - Redirecting to: {oidc_url}")
    
    return RedirectResponse(oidc_url, status_code=302)

@router.post("/lti/launch")
async def lti_launch(request: Request):
    """
    LTI launch endpoint (validates JWT, creates session, redirects to chat UI)
    
    Flow:
    1. Validate JWT signature and claims
    2. Create/update user in MongoDB
    3. Create/retrieve session
    4. Map Moodle course to chatbot subject
    5. Redirect to chat UI with session token
    """
    try:
        # Parse form data (id_token, state)
        form = await request.form()
        
        id_token = form.get("id_token")
        
        if not id_token:
            logger.error("Missing id_token in LTI launch")
            raise HTTPException(status_code=400, detail="Missing id_token")
        
        # Step 1: Validate JWT
        logger.info("Validating JWT token...")
        try:
            decoded = jwt_validator.validate_jwt(id_token)
        except Exception as e:
            logger.error(f"JWT validation failed: {e}")
            raise HTTPException(status_code=401, detail=f"JWT validation failed: {e}")
        
        # Step 2: Extract LTI claims
        lti_user_id = decoded.get("sub")
        email = decoded.get("email", "")
        name = decoded.get("name", "LTI User")
        given_name = decoded.get("given_name", "")
        family_name = decoded.get("family_name", "")
        
        
        # Extract context (course) information
        context_claim = decoded.get("https://purl.imsglobal.org/spec/lti/claim/context", {})
        context_id = context_claim.get("id", "")
        context_label = context_claim.get("label", "")
        context_title = context_claim.get("title", "Unknown Course")
        
        # Extract resource link (activity) information        
        logger.info(f"LTI Launch - User: {lti_user_id}, Course: {context_label} ({context_title})")
        
        # Step 3: Create or update user in MongoDB
        user = await user_service.create_or_update_user(
            lti_user_id=lti_user_id,
            email=email,
            name=name,
            given_name=given_name,
            family_name=family_name
        )
        
        # Handle both '_id' (MongoDB) and 'id' (user-service API response)
        user_id = user.get('_id') or user.get('id') if user else None
        
        if not user or not user_id:
            logger.error(f"Failed to create/retrieve user for LTI user {lti_user_id}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to create user account. Please contact support."
            )
        
        logger.info(f"User created/updated: {user.get('name')} (ID: {user_id})")
        
        # Step 4: Map course to subject
        subject = COURSE_SUBJECT_MAPPING.get(context_label, context_label.lower().replace(" ", "_"))
        
        logger.info(f"Mapped course '{context_label}' to subject: {subject}")
        
        # Step 5: Create or retrieve session
        session = await session_service.create_or_get_session(
            user_id=str(user_id),  # Use the extracted user_id (works with both 'id' and '_id')
            lti_user_id=lti_user_id,
            context_id=context_id,
            context_label=context_label,
            subject=subject
        )
        
        session_token = session.get("session_token")
        logger.info(f"Session created/retrieved: {session_token}")
        
        # Step 6: Build redirect URL to chat UI
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        
        # Option 1: Redirect with query params (for iframe embedding)
        redirect_url = f"{frontend_url}/?session_token={session_token}&lti=true&subject={subject}"
        
        logger.info(f"Redirecting to chat UI: {redirect_url}")
        
        # Return HTML with auto-redirect (works better in iframe than RedirectResponse)
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Loading Chat...</title>
            <script>
                // Auto-redirect to chat UI
                window.location.href = "{redirect_url}";
            </script>
        </head>
        <body>
            <p>Loading chat interface...</p>
            <p>If you are not redirected, <a href="{redirect_url}">click here</a>.</p>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LTI launch error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"LTI launch failed: {str(e)}")
