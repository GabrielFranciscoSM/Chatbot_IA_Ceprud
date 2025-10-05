#!/usr/bin/env python3
"""
Quick syntax check for Phase 3 integration
"""

import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

print("Testing imports...")

try:
    from lti.routes import router
    print("✓ LTI routes imported successfully")
except Exception as e:
    print(f"✗ Failed to import LTI routes: {e}")
    sys.exit(1)

try:
    from lti.jwt_validator import LTIJWTValidator
    print("✓ JWT validator imported successfully")
except Exception as e:
    print(f"✗ Failed to import JWT validator: {e}")
    sys.exit(1)

try:
    from lti.user_service import LTIUserService
    print("✓ User service imported successfully")
except Exception as e:
    print(f"✗ Failed to import user service: {e}")
    sys.exit(1)

try:
    from lti.session_service import LTISessionService
    print("✓ Session service imported successfully")
except Exception as e:
    print(f"✗ Failed to import session service: {e}")
    sys.exit(1)

try:
    from lti.config import LTIConfig
    print("✓ LTI config imported successfully")
except Exception as e:
    print(f"✗ Failed to import LTI config: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("All Phase 3 components imported successfully!")
print("="*60)
print("\nPhase 3 integration is ready.")
print("Next: Start the server and test with Moodle.")
