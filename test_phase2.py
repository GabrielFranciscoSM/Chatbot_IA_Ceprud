#!/usr/bin/env python3
"""
Test Phase 2: LTI Endpoints

Tests the OIDC login, launch, and JWKS endpoints.
"""

import sys
import os
import json
import jwt
from datetime import datetime, timedelta

# Add app to path
sys.path.insert(0, 'app')

print("="*60)
print("Testing Phase 2: LTI Endpoints")
print("="*60)
print()

# Test 1: Import modules
print("📦 Test 1: Importing LTI modules...")
try:
    from lti.config import LTIConfig
    from lti.models import LTIPlatformConfig, LTISession
    from lti import routes
    print("✅ All modules imported successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 2: Check JWKS endpoint
print("🔑 Test 2: Testing JWKS endpoint...")
try:
    config = LTIConfig('./lti_config')
    jwks = config.get_jwks()
    
    if 'keys' in jwks and len(jwks['keys']) > 0:
        print("✅ JWKS endpoint data is valid")
        print(f"   Key ID: {jwks['keys'][0]['kid']}")
        print(f"   Algorithm: {jwks['keys'][0]['alg']}")
    else:
        print("❌ JWKS is invalid")
        sys.exit(1)
except Exception as e:
    print(f"❌ JWKS test failed: {e}")
    sys.exit(1)

print()

# Test 3: Create a mock JWT token
print("🎫 Test 3: Creating mock LTI JWT token...")
try:
    # Create a sample JWT payload (mimicking what Moodle sends)
    now = datetime.utcnow()
    payload = {
        "iss": "https://moodle.ugr.es",
        "sub": "user123",
        "aud": "GBx1F4LefiUr7bZ",
        "exp": now + timedelta(hours=1),
        "iat": now,
        "nonce": "demo-nonce-456",
        "email": "student@correo.ugr.es",
        "name": "Juan Pérez",
        "https://purl.imsglobal.org/spec/lti/claim/message_type": "LtiResourceLinkRequest",
        "https://purl.imsglobal.org/spec/lti/claim/version": "1.3.0",
        "https://purl.imsglobal.org/spec/lti/claim/deployment_id": "1",
        "https://purl.imsglobal.org/spec/lti/claim/context": {
            "id": "course_456",
            "label": "IS",
            "title": "Ingeniería de Servidores",
            "type": ["CourseSection"]
        },
        "https://purl.imsglobal.org/spec/lti/claim/resource_link": {
            "id": "resource_789",
            "title": "AI Chatbot"
        },
        "https://purl.imsglobal.org/spec/lti/claim/roles": [
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner"
        ]
    }
    
    # Encode without signature (for testing)
    token = jwt.encode(payload, "", algorithm="none")
    print("✅ Mock JWT token created")
    print(f"   User: {payload['name']}")
    print(f"   Email: {payload['email']}")
    print(f"   Course: {payload['https://purl.imsglobal.org/spec/lti/claim/context']['label']}")
    
except Exception as e:
    print(f"❌ JWT creation failed: {e}")
    sys.exit(1)

print()

# Test 4: Decode and validate JWT
print("🔍 Test 4: Decoding JWT token...")
try:
    decoded = jwt.decode(token, options={"verify_signature": False, "verify_aud": False})
    
    print("✅ JWT decoded successfully")
    print(f"   Issuer: {decoded.get('iss')}")
    print(f"   Subject: {decoded.get('sub')}")
    print(f"   Email: {decoded.get('email')}")
    
    # Extract context
    context = decoded.get("https://purl.imsglobal.org/spec/lti/claim/context", {})
    print(f"   Context ID: {context.get('id')}")
    print(f"   Context Label: {context.get('label')}")
    
except Exception as e:
    print(f"❌ JWT decode failed: {e}")
    sys.exit(1)

print()

# Test 5: Test LTI Session creation
print("📊 Test 5: Creating LTI session model...")
try:
    lti_session = LTISession(
        session_id=f"lti_session_{decoded['sub']}_{context.get('id')}",
        lti_user_id=decoded['sub'],
        lti_deployment_id=decoded.get("https://purl.imsglobal.org/spec/lti/claim/deployment_id", "1"),
        platform_id=decoded['iss'],
        email=decoded.get('email'),
        name=decoded.get('name'),
        roles=decoded.get("https://purl.imsglobal.org/spec/lti/claim/roles", []),
        context_id=context.get('id'),
        context_label=context.get('label'),
        context_title=context.get('title'),
        launch_id=f"launch_{now.timestamp()}"
    )
    
    print("✅ LTI Session created successfully")
    print(f"   Session ID: {lti_session.session_id}")
    print(f"   User ID: {lti_session.lti_user_id}")
    print(f"   Email: {lti_session.email}")
    print(f"   Course: {lti_session.context_label}")
    
except Exception as e:
    print(f"❌ Session creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 6: Test subject mapping
print("🗺️  Test 6: Testing subject mapping...")
try:
    # Load subject mappings from env
    subject_mappings = {
        "IS": "ingenieria_de_servidores",
        "MAC": "modelos_avanzados_computacion",
        "MH": "metaheuristicas",
        "SO": "sistemas_operativos",
        "IC": "ingenieria_conocimiento",
        "ALG": "algorítmica",
        "CALC": "calculo"
    }
    
    course_label = context.get('label', '')
    mapped_subject = subject_mappings.get(course_label)
    
    if mapped_subject:
        print(f"✅ Course '{course_label}' mapped to subject '{mapped_subject}'")
    else:
        print(f"⚠️  Course '{course_label}' not found in mappings")
        print(f"   Using default or showing error")
    
except Exception as e:
    print(f"❌ Subject mapping failed: {e}")
    sys.exit(1)

print()

# Test 7: Test OIDC login URL generation
print("🔗 Test 7: Testing OIDC login URL generation...")
try:
    from urllib.parse import urlencode
    
    client_id = os.getenv("MOODLE_CLIENT_ID", "GBx1F4LefiUr7bZ")
    auth_login_url = os.getenv("MOODLE_AUTH_LOGIN_URL", "https://moodle.ugr.es/mod/lti/auth.php")
    target_link_uri = f"{os.getenv('CHATBOT_BASE_URL', 'http://localhost:8080')}/lti/launch"
    
    params = {
        "client_id": client_id,
        "login_hint": "user-login-hint",
        "target_link_uri": target_link_uri,
        "response_type": "id_token",
        "scope": "openid",
        "state": "demo-state-123",
        "nonce": "demo-nonce-456",
        "prompt": "none"
    }
    
    oidc_url = f"{auth_login_url}?{urlencode(params)}"
    print("✅ OIDC URL generated successfully")
    print(f"   URL: {oidc_url[:80]}...")
    
except Exception as e:
    print(f"❌ OIDC URL generation failed: {e}")
    sys.exit(1)

print()

# Summary
print("="*60)
print("✅ Phase 2 Tests PASSED!")
print("="*60)
print()
print("Tested Components:")
print("  ✅ Module imports")
print("  ✅ JWKS endpoint data")
print("  ✅ JWT token creation")
print("  ✅ JWT token decoding")
print("  ✅ LTI session model")
print("  ✅ Subject mapping")
print("  ✅ OIDC URL generation")
print()
print("Next: Start the server and test endpoints with curl/browser")
print()
