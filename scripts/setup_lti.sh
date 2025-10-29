#!/bin/bash

# LTI 1.3 Setup Script
# This script installs dependencies and generates the necessary keys for LTI integration

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "LTI 1.3 Integration Setup"
echo "=========================================="
echo ""

# Step 1: Install Python dependencies
echo "📦 Installing LTI dependencies..."
pip install PyLTI1p3==2.0.0 PyJWT==2.10.1 cryptography==46.0.2 jwcrypto==1.5.6

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""

# Step 2: Generate RSA keys
echo "🔑 Generating RSA key pair for LTI..."
python3 -c "
from app.lti.config import LTIConfig
import os

config_dir = './lti_config'
config = LTIConfig(config_dir)
print(f'✅ Keys generated in {config_dir}/')
print(f'   - Private key: {config.private_key_path}')
print(f'   - Public key: {config.public_key_path}')
print(f'   - JWKS: {config.jwks_path}')
"

if [ $? -eq 0 ]; then
    echo "✅ Keys generated successfully"
else
    echo "❌ Failed to generate keys"
    exit 1
fi

echo ""

# Step 3: Display JWKS URL
echo "📋 Your LTI configuration:"
echo "   OIDC Login URL: http://localhost:8080/lti/login"
echo "   Launch URL: http://localhost:8080/lti/launch"
echo "   JWKS URL: http://localhost:8080/lti/jwks"
echo ""
echo "   ⚠️  NOTE: Replace 'localhost:8080' with your actual domain in production"

echo ""
echo "=========================================="
echo "✅ LTI Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Copy the JWKS URL above"
echo "2. Configure Moodle with these URLs"
echo "3. Update moodle/.env with your Moodle instance details"
echo "4. Start the application with LTI support"
echo ""
