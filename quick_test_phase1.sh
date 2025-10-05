#!/bin/bash
# Quick test to verify Phase 1 is working

cd /home/gabriel/clase/TFG/Practicas/Chatbot_IA_Ceprud

echo "🧪 Quick Phase 1 Test"
echo "===================="
echo ""

# Test 1: Check keys exist
if [ -f "lti_config/private_key.pem" ] && [ -f "lti_config/public_key.pem" ] && [ -f "lti_config/jwks.json" ]; then
    echo "✅ All LTI keys generated"
else
    echo "❌ Keys missing - run: .venv/bin/python -c 'import sys; sys.path.insert(0, \"app\"); from lti.config import LTIConfig; LTIConfig(\"./lti_config\")'"
    exit 1
fi

# Test 2: Validate JWKS
.venv/bin/python << 'EOF'
import sys, json
sys.path.insert(0, 'app')
from lti.config import LTIConfig
config = LTIConfig('./lti_config')
jwks = config.get_jwks()
print(f"✅ JWKS valid (Key ID: {jwks['keys'][0]['kid']})")
EOF

if [ $? -ne 0 ]; then
    echo "❌ JWKS validation failed"
    exit 1
fi

echo ""
echo "✅ Phase 1 is working correctly!"
echo ""
echo "LTI Endpoints (for Moodle):"
echo "  - JWKS: http://150.214.22.87:8080/lti/jwks"
echo "  - Login: http://150.214.22.87:8080/lti/login"
echo "  - Launch: http://150.214.22.87:8080/lti/launch"
