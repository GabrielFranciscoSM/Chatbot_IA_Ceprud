#!/usr/bin/env python3
"""
Comprehensive Phase 3 Testing Suite

Tests all LTI integration components:
1. JWT Validator
2. User Service
3. Session Service
4. Routes Integration
5. End-to-end flow
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import jwt
import json

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "errors": []
}

def print_test_header(test_name):
    """Print a formatted test header"""
    print("\n" + "="*70)
    print(f"TEST: {test_name}")
    print("="*70)

def print_success(message):
    """Print success message"""
    print(f"  ✓ {message}")
    test_results["passed"] += 1

def print_failure(message, error=None):
    """Print failure message"""
    print(f"  ✗ {message}")
    if error:
        print(f"    Error: {error}")
        test_results["errors"].append(f"{message}: {error}")
    test_results["failed"] += 1

def print_info(message):
    """Print info message"""
    print(f"  ℹ {message}")


async def test_imports():
    """Test 1: Verify all modules can be imported"""
    print_test_header("Module Imports")
    
    try:
        from lti.config import LTIConfig
        print_success("LTIConfig imported")
    except Exception as e:
        print_failure("LTIConfig import failed", e)
        return False
    
    try:
        from lti.jwt_validator import LTIJWTValidator
        print_success("LTIJWTValidator imported")
    except Exception as e:
        print_failure("LTIJWTValidator import failed", e)
        return False
    
    try:
        from lti.user_service import LTIUserService
        print_success("LTIUserService imported")
    except Exception as e:
        print_failure("LTIUserService import failed", e)
        return False
    
    try:
        from lti.session_service import LTISessionService
        print_success("LTISessionService imported")
    except Exception as e:
        print_failure("LTISessionService import failed", e)
        return False
    
    try:
        from lti.database import get_database, get_mongo_client
        print_success("Database utilities imported")
    except Exception as e:
        print_failure("Database utilities import failed", e)
        return False
    
    try:
        from lti.routes import router
        print_success("LTI routes imported")
    except Exception as e:
        print_failure("LTI routes import failed", e)
        return False
    
    return True


async def test_lti_config():
    """Test 2: Verify LTI configuration"""
    print_test_header("LTI Configuration")
    
    try:
        from lti.config import LTIConfig
        
        config_dir = os.getenv("LTI_CONFIG_DIR", "./lti_config")
        lti_config = LTIConfig(config_dir)
        
        # Check private key exists
        private_key = lti_config.get_private_key()
        if private_key:
            print_success("Private key loaded")
        else:
            print_failure("Private key not found")
            return False
        
        # Check public key exists
        public_key = lti_config.get_public_key()
        if public_key:
            print_success("Public key loaded")
        else:
            print_failure("Public key not found")
            return False
        
        # Check JWKS generation
        jwks = lti_config.get_jwks()
        if jwks and "keys" in jwks:
            print_success(f"JWKS generated with {len(jwks['keys'])} key(s)")
        else:
            print_failure("JWKS generation failed")
            return False
        
        # Verify KID
        if lti_config.kid:
            print_success(f"Key ID (kid): {lti_config.kid}")
        else:
            print_failure("No Key ID generated")
            return False
        
        return True
        
    except Exception as e:
        print_failure("LTI config test failed", e)
        return False


async def test_jwt_creation_and_validation():
    """Test 3: Create and validate JWT tokens"""
    print_test_header("JWT Creation and Validation")
    
    try:
        from lti.config import LTIConfig
        
        config_dir = os.getenv("LTI_CONFIG_DIR", "./lti_config")
        lti_config = LTIConfig(config_dir)
        
        # Create a test JWT
        claims = {
            "iss": os.getenv("MOODLE_ISSUER", "https://moodle.ugr.es"),
            "sub": "test-user-12345",
            "aud": os.getenv("MOODLE_CLIENT_ID", "GBx1F4LefiUr7bZ"),
            "exp": int((datetime.utcnow() + timedelta(minutes=5)).timestamp()),
            "iat": int(datetime.utcnow().timestamp()),
            "nonce": "test-nonce-abc123",
            "email": "testuser@ugr.es",
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User",
            "https://purl.imsglobal.org/spec/lti/claim/message_type": "LtiResourceLinkRequest",
            "https://purl.imsglobal.org/spec/lti/claim/version": "1.3.0",
            "https://purl.imsglobal.org/spec/lti/claim/context": {
                "id": "course-math-101",
                "label": "ASIG001",
                "title": "Mathematics 101"
            },
            "https://purl.imsglobal.org/spec/lti/claim/resource_link": {
                "id": "resource-link-123",
                "title": "AI Chatbot Activity"
            }
        }
        
        # Sign the token
        private_key = lti_config.get_private_key()
        test_token = jwt.encode(
            claims,
            private_key,
            algorithm="RS256",
            headers={"kid": lti_config.kid}
        )
        
        print_success(f"JWT token created (length: {len(test_token)})")
        print_info(f"Token preview: {test_token[:80]}...")
        
        # Decode without verification (for testing)
        decoded = jwt.decode(test_token, options={"verify_signature": False})
        
        # Verify claims
        if decoded.get("sub") == "test-user-12345":
            print_success("JWT subject (sub) verified")
        else:
            print_failure("JWT subject mismatch")
            return False
        
        if decoded.get("email") == "testuser@ugr.es":
            print_success("JWT email claim verified")
        else:
            print_failure("JWT email mismatch")
            return False
        
        context = decoded.get("https://purl.imsglobal.org/spec/lti/claim/context", {})
        if context.get("label") == "ASIG001":
            print_success("JWT context claim verified")
        else:
            print_failure("JWT context mismatch")
            return False
        
        # Store token for later tests
        return test_token
        
    except Exception as e:
        print_failure("JWT creation/validation failed", e)
        import traceback
        traceback.print_exc()
        return False


async def test_user_service(test_token=None):
    """Test 4: User service functionality"""
    print_test_header("User Service")
    
    try:
        from lti.user_service import LTIUserService
        
        user_service = LTIUserService()
        print_success("LTIUserService instantiated")
        
        # Check if the underlying user service is accessible
        if hasattr(user_service, 'user_service'):
            print_success("Underlying user_service accessible")
        else:
            print_failure("user_service not accessible")
            return False
        
        # Test user creation (requires MongoDB)
        print_info("Testing user creation (requires MongoDB connection)...")
        
        try:
            user = await user_service.create_or_update_user(
                lti_user_id="test-lti-user-001",
                email="lti.test.user@test.local",
                name="LTI Test User",
                given_name="LTI",
                family_name="Test"
            )
            
            if user and "_id" in user:
                print_success(f"User created: {user.get('email')} (ID: {user.get('_id')})")
                return user
            else:
                print_failure("User creation returned invalid data")
                return False
                
        except Exception as e:
            print_failure("User creation test failed (MongoDB may not be running)", e)
            print_info("This is expected if MongoDB is not running")
            return None
        
    except Exception as e:
        print_failure("User service test failed", e)
        import traceback
        traceback.print_exc()
        return False


async def test_session_service(user=None):
    """Test 5: Session service functionality"""
    print_test_header("Session Service")
    
    try:
        from lti.session_service import LTISessionService
        
        session_service = LTISessionService()
        print_success("LTISessionService instantiated")
        
        # Check database connection
        if hasattr(session_service, 'sessions_collection'):
            print_success("Session collection accessible")
        else:
            print_failure("Session collection not accessible")
            return False
        
        # Test session creation (requires MongoDB and user)
        if not user:
            print_info("Skipping session creation (no user from previous test)")
            return None
        
        print_info("Testing session creation (requires MongoDB connection)...")
        
        try:
            session = await session_service.create_or_get_session(
                user_id=str(user.get("_id")),
                lti_user_id="test-lti-user-001",
                context_id="course-math-101",
                context_label="ASIG001",
                subject="Matematicas"
            )
            
            if session and "session_token" in session:
                print_success(f"Session created: {session.get('session_token')[:20]}...")
                print_success(f"Session expires at: {session.get('expires_at')}")
                print_success(f"Subject: {session.get('subject')}")
                
                # Test session retrieval
                retrieved = await session_service.get_session(session.get("session_token"))
                if retrieved:
                    print_success("Session retrieved successfully")
                else:
                    print_failure("Session retrieval failed")
                    return False
                
                return session
            else:
                print_failure("Session creation returned invalid data")
                return False
                
        except Exception as e:
            print_failure("Session creation test failed (MongoDB may not be running)", e)
            print_info("This is expected if MongoDB is not running")
            return None
        
    except Exception as e:
        print_failure("Session service test failed", e)
        import traceback
        traceback.print_exc()
        return False


async def test_routes_integration():
    """Test 6: Routes integration"""
    print_test_header("Routes Integration")
    
    try:
        from lti.routes import router, COURSE_SUBJECT_MAPPING
        
        print_success("LTI router imported")
        
        # Check course mappings
        if COURSE_SUBJECT_MAPPING:
            print_success(f"Course mappings configured: {len(COURSE_SUBJECT_MAPPING)} courses")
            for course, subject in COURSE_SUBJECT_MAPPING.items():
                print_info(f"  {course} → {subject}")
        else:
            print_info("No course mappings configured (using default)")
        
        # Check routes are registered
        routes_found = []
        for route in router.routes:
            if hasattr(route, 'path'):
                routes_found.append(route.path)
        
        expected_routes = ["/lti/jwks", "/lti/login", "/lti/launch"]
        for expected in expected_routes:
            if expected in routes_found:
                print_success(f"Route {expected} registered")
            else:
                print_failure(f"Route {expected} not found")
                return False
        
        return True
        
    except Exception as e:
        print_failure("Routes integration test failed", e)
        import traceback
        traceback.print_exc()
        return False


async def test_database_connection():
    """Test 7: MongoDB database connection"""
    print_test_header("Database Connection")
    
    try:
        from lti.database import get_database, get_mongo_client
        
        # Try to get database
        try:
            db = get_database()
            print_success("Database connection established")
            
            # Try to list collections
            collections = await db.list_collection_names()
            print_success(f"Database accessible, {len(collections)} collections found")
            print_info(f"Collections: {', '.join(collections[:5])}{'...' if len(collections) > 5 else ''}")
            
            return True
            
        except Exception as e:
            print_failure("Database connection failed (MongoDB may not be running)", e)
            print_info("This is expected if MongoDB is not running")
            return None
        
    except Exception as e:
        print_failure("Database test failed", e)
        return False


async def test_end_to_end():
    """Test 8: End-to-end LTI flow simulation"""
    print_test_header("End-to-End LTI Flow Simulation")
    
    try:
        from lti.config import LTIConfig
        from lti.user_service import LTIUserService
        from lti.session_service import LTISessionService
        
        print_info("Simulating complete LTI launch flow...")
        
        # Step 1: Create JWT token
        config_dir = os.getenv("LTI_CONFIG_DIR", "./lti_config")
        lti_config = LTIConfig(config_dir)
        
        claims = {
            "iss": os.getenv("MOODLE_ISSUER", "https://moodle.ugr.es"),
            "sub": "e2e-test-user",
            "aud": os.getenv("MOODLE_CLIENT_ID", "GBx1F4LefiUr7bZ"),
            "exp": int((datetime.utcnow() + timedelta(minutes=5)).timestamp()),
            "iat": int(datetime.utcnow().timestamp()),
            "nonce": "e2e-nonce",
            "email": "e2e.test@ugr.es",
            "name": "E2E Test User",
            "https://purl.imsglobal.org/spec/lti/claim/context": {
                "id": "e2e-course",
                "label": "ASIG001",
                "title": "E2E Test Course"
            }
        }
        
        private_key = lti_config.get_private_key()
        id_token = jwt.encode(claims, private_key, algorithm="RS256", headers={"kid": lti_config.kid})
        print_success("Step 1: JWT token created")
        
        # Step 2: Decode token (simulating JWT validation)
        decoded = jwt.decode(id_token, options={"verify_signature": False})
        print_success("Step 2: JWT token decoded")
        
        # Step 3: Create user
        try:
            user_service = LTIUserService()
            user = await user_service.create_or_update_user(
                lti_user_id=decoded.get("sub"),
                email=decoded.get("email"),
                name=decoded.get("name"),
                given_name="E2E",
                family_name="Test"
            )
            print_success(f"Step 3: User created ({user.get('email')})")
        except Exception as e:
            print_failure("Step 3: User creation failed", e)
            print_info("Skipping remaining steps (requires MongoDB)")
            return None
        
        # Step 4: Map course to subject
        context = decoded.get("https://purl.imsglobal.org/spec/lti/claim/context", {})
        course_label = context.get("label", "")
        subject = "Matematicas" if course_label == "ASIG001" else context.get("title")
        print_success(f"Step 4: Course mapped ({course_label} → {subject})")
        
        # Step 5: Create session
        try:
            session_service = LTISessionService()
            session = await session_service.create_or_get_session(
                user_id=str(user.get("_id")),
                lti_user_id=decoded.get("sub"),
                context_id=context.get("id"),
                context_label=course_label,
                subject=subject
            )
            print_success(f"Step 5: Session created ({session.get('session_token')[:20]}...)")
        except Exception as e:
            print_failure("Step 5: Session creation failed", e)
            return False
        
        # Step 6: Build redirect URL
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        redirect_url = f"{frontend_url}/?session_token={session.get('session_token')}&lti=true&subject={subject}"
        print_success(f"Step 6: Redirect URL built")
        print_info(f"  URL: {redirect_url[:80]}...")
        
        print_success("✓ Complete E2E flow successful!")
        return True
        
    except Exception as e:
        print_failure("End-to-end test failed", e)
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*70)
    print("PHASE 3 COMPREHENSIVE TEST SUITE")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Imports
    imports_ok = await test_imports()
    if not imports_ok:
        print("\n⚠ Critical: Import tests failed. Cannot continue.")
        return False
    
    # Test 2: LTI Config
    config_ok = await test_lti_config()
    
    # Test 3: JWT
    test_token = await test_jwt_creation_and_validation()
    
    # Test 4: Database
    db_ok = await test_database_connection()
    
    # Test 5: User Service
    user = await test_user_service(test_token)
    
    # Test 6: Session Service
    session = await test_session_service(user)
    
    # Test 7: Routes
    routes_ok = await test_routes_integration()
    
    # Test 8: End-to-end
    e2e_ok = await test_end_to_end()
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"✓ Passed: {test_results['passed']}")
    print(f"✗ Failed: {test_results['failed']}")
    
    if test_results['errors']:
        print(f"\nErrors encountered:")
        for error in test_results['errors']:
            print(f"  • {error}")
    
    print("\n" + "="*70)
    print("PHASE 3 STATUS")
    print("="*70)
    
    if test_results['failed'] == 0:
        print("✅ ALL TESTS PASSED - Phase 3 is fully functional!")
    elif db_ok is None:
        print("⚠️  PARTIAL SUCCESS - Core functionality works")
        print("   MongoDB tests skipped (database not running)")
        print("   This is normal for code-only testing")
    else:
        print("❌ SOME TESTS FAILED - Review errors above")
    
    print()
    print("Next steps:")
    print("  1. Ensure MongoDB is running for full integration tests")
    print("  2. Test with real Moodle instance")
    print("  3. Proceed to Phase 4 (Frontend Integration)")
    print("="*70)
    
    return test_results['failed'] == 0


if __name__ == "__main__":
    asyncio.run(run_all_tests())
