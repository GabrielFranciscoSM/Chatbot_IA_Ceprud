#!/bin/bash

# Test Phase 1: LTI Infrastructure
# This script tests that all Phase 1 components are working correctly

echo "=========================================="
echo "Testing Phase 1: LTI Infrastructure"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Run this script from the project root directory"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "🔧 Activating virtual environment..."
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
    echo ""
elif [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
    echo "✅ Virtual environment activated"
    echo ""
else
    echo "⚠️  No virtual environment found, using system Python"
    echo ""
fi

# Test 1: Check dependencies
echo "📦 Test 1: Checking LTI dependencies..."
python3 -c "
import sys
try:
    import pylti1p3
    print('✅ PyLTI1p3:', pylti1p3.__version__)
except ImportError as e:
    print('❌ PyLTI1p3 not installed')
    sys.exit(1)

try:
    import jwt
    print('✅ PyJWT installed')
except ImportError:
    print('❌ PyJWT not installed')
    sys.exit(1)

try:
    import cryptography
    print('✅ Cryptography installed')
except ImportError:
    print('❌ Cryptography not installed')
    sys.exit(1)

try:
    import jwcrypto
    print('✅ jwcrypto installed')
except ImportError:
    print('❌ jwcrypto not installed')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Dependencies not installed. Run:"
    echo "   pip install -r requirements.txt"
    exit 1
fi

echo ""

# Test 2: Check LTI module structure
echo "📂 Test 2: Checking LTI module structure..."
if [ -f "app/lti/__init__.py" ]; then
    echo "✅ app/lti/__init__.py exists"
else
    echo "❌ app/lti/__init__.py missing"
    exit 1
fi

if [ -f "app/lti/models.py" ]; then
    echo "✅ app/lti/models.py exists"
else
    echo "❌ app/lti/models.py missing"
    exit 1
fi

if [ -f "app/lti/config.py" ]; then
    echo "✅ app/lti/config.py exists"
else
    echo "❌ app/lti/config.py missing"
    exit 1
fi

if [ -f "app/lti/routes.py" ]; then
    echo "✅ app/lti/routes.py exists"
else
    echo "❌ app/lti/routes.py missing"
    exit 1
fi

echo ""

# Test 3: Generate RSA keys
echo "🔑 Test 3: Generating RSA key pair..."
python3 << 'PYTHON_SCRIPT'
import sys
import os

# Add app directory to path
sys.path.insert(0, 'app')

try:
    from lti.config import LTIConfig
    
    config_dir = './lti_config'
    config = LTIConfig(config_dir)
    
    print(f'✅ Keys generated successfully')
    print(f'   📁 Config directory: {config_dir}/')
    
    if os.path.exists(config.private_key_path):
        print(f'   ✅ Private key: {config.private_key_path}')
    else:
        print(f'   ❌ Private key missing')
        sys.exit(1)
    
    if os.path.exists(config.public_key_path):
        print(f'   ✅ Public key: {config.public_key_path}')
    else:
        print(f'   ❌ Public key missing')
        sys.exit(1)
    
    if os.path.exists(config.jwks_path):
        print(f'   ✅ JWKS: {config.jwks_path}')
    else:
        print(f'   ❌ JWKS missing')
        sys.exit(1)
        
except Exception as e:
    print(f'❌ Error generating keys: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON_SCRIPT

if [ $? -ne 0 ]; then
    echo "❌ Key generation failed"
    exit 1
fi

echo ""

# Test 4: Verify JWKS format
echo "📋 Test 4: Verifying JWKS format..."
python3 << 'PYTHON_SCRIPT'
import sys
import json
sys.path.insert(0, 'app')

from lti.config import LTIConfig

try:
    config = LTIConfig('./lti_config')
    jwks = config.get_jwks()
    
    # Check JWKS structure
    if 'keys' not in jwks:
        print('❌ JWKS missing "keys" field')
        sys.exit(1)
    
    if len(jwks['keys']) == 0:
        print('❌ JWKS has no keys')
        sys.exit(1)
    
    key = jwks['keys'][0]
    required_fields = ['kty', 'n', 'e', 'kid', 'alg', 'use']
    
    for field in required_fields:
        if field not in key:
            print(f'❌ JWKS key missing required field: {field}')
            sys.exit(1)
    
    print('✅ JWKS format is valid')
    print(f'   Key ID: {key["kid"]}')
    print(f'   Algorithm: {key["alg"]}')
    print(f'   Use: {key["use"]}')
    
except Exception as e:
    print(f'❌ Error verifying JWKS: {e}')
    sys.exit(1)
PYTHON_SCRIPT

if [ $? -ne 0 ]; then
    echo "❌ JWKS verification failed"
    exit 1
fi

echo ""

# Test 5: Test LTI models
echo "📊 Test 5: Testing LTI data models..."
python3 << 'PYTHON_SCRIPT'
import sys
sys.path.insert(0, 'app')

from lti.models import LTIPlatformConfig, LTISession
from datetime import datetime

try:
    # Test LTIPlatformConfig
    platform_config = LTIPlatformConfig(
        platform_id="https://moodle.test.com",
        client_id="test123",
        auth_login_url="https://moodle.test.com/auth",
        auth_token_url="https://moodle.test.com/token",
        key_set_url="https://moodle.test.com/jwks",
        deployment_ids=["1"]
    )
    print('✅ LTIPlatformConfig model works')
    
    # Test LTISession
    lti_session = LTISession(
        session_id="test_session",
        lti_user_id="user123",
        lti_deployment_id="1",
        platform_id="https://moodle.test.com",
        launch_id="launch123"
    )
    print('✅ LTISession model works')
    
except Exception as e:
    print(f'❌ Model validation error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON_SCRIPT

if [ $? -ne 0 ]; then
    echo "❌ Model testing failed"
    exit 1
fi

echo ""

# Test 6: Display configuration
echo "⚙️  Test 6: LTI Configuration Summary..."
python3 << 'PYTHON_SCRIPT'
import sys
import os
sys.path.insert(0, 'app')

from lti.config import LTIConfig

config = LTIConfig('./lti_config')
base_url = os.getenv('CHATBOT_BASE_URL', 'http://localhost:8080')

tool_config = config.get_tool_config(base_url)

print('✅ Tool Configuration:')
print(f'   Title: {tool_config["title"]}')
print(f'   OIDC Login URL: {tool_config["oidc_initiation_url"]}')
print(f'   Launch URL: {tool_config["target_link_uri"]}')
print(f'   JWKS URL: {tool_config["public_jwk_url"]}')
PYTHON_SCRIPT

echo ""

# Final summary
echo "=========================================="
echo "✅ Phase 1 Tests Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Update moodle/.env with your Moodle details"
echo "2. Start the application to test endpoints"
echo "3. Proceed to Phase 2 for endpoint implementation"
echo ""
echo "To test the endpoints, run:"
echo "  python app/app.py"
echo "  curl http://localhost:8080/lti/jwks"
echo ""
