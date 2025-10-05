#!/usr/bin/env python3
"""
Create Test LTI Session for Local Testing

This script creates a test user and LTI session in MongoDB
so you can test the frontend LTI mode locally.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

async def create_test_session():
    """Create test user and LTI session"""
    from motor.motor_asyncio import AsyncIOMotorClient
    from bson import ObjectId
    
    print("🔧 Creating test LTI session...\n")
    
    # Connect directly to MongoDB with credentials
    mongo_uri = os.getenv("MONGO_URI", "mongodb://admin:password123@localhost:27017")
    client = AsyncIOMotorClient(mongo_uri)
    db = client["chatbot_users"]
    
    users_collection = db["users"]
    sessions_collection = db["lti_sessions"]
    
    # Test data
    test_email = "test@ugr.es"
    test_name = "Test User LTI"
    test_subject = "ingenieria_de_servidores"
    test_course_label = "IS-2025-TEST"
    
    print(f"📧 Email: {test_email}")
    print(f"👤 Name: {test_name}")
    print(f"📚 Subject: {test_subject}")
    print(f"🎓 Course: {test_course_label}\n")
    
    # Step 1: Create or get user
    print("Step 1: Creating/getting user...")
    try:
        # Check if user exists
        existing_user = await users_collection.find_one({"email": test_email})
        
        if existing_user:
            user = existing_user
            print(f"✅ User found: {user.get('email')} (ID: {user.get('_id')})")
        else:
            # Create new user
            user_doc = {
                "email": test_email,
                "name": test_name,
                "given_name": "Test",
                "family_name": "User",
                "role": "Learner",
                "lti_user_id": "test_lti_user_123",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            result = await users_collection.insert_one(user_doc)
            user_doc["_id"] = result.inserted_id
            user = user_doc
            print(f"✅ User created: {user.get('email')} (ID: {user.get('_id')})")
        
        print()
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        client.close()
        return None
    
    # Step 2: Create session
    print("Step 2: Creating LTI session...")
    try:
        import secrets
        from datetime import datetime, timedelta
        
        # Generate session token
        session_token = "TEST_SESSION_" + secrets.token_urlsafe(16)
        
        # Check if session already exists for this user/context
        existing_session = await sessions_collection.find_one({
            "user_id": str(user["_id"]),
            "context_id": "test_course_456",
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if existing_session:
            session = existing_session
            print(f"✅ Existing session found!")
        else:
            # Create new session
            session_doc = {
                "session_token": session_token,
                "user_id": str(user["_id"]),
                "lti_user_id": "test_lti_user_123",
                "context_id": "test_course_456",
                "context_label": test_course_label,
                "subject": test_subject,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=8)
            }
            result = await sessions_collection.insert_one(session_doc)
            session_doc["_id"] = result.inserted_id
            session = session_doc
            print(f"✅ Session created!")
        
        session_token = session.get("session_token")
        expires_at = session.get("expires_at")
        
        print(f"   Token: {session_token}")
        print(f"   Expires: {expires_at}\n")
        
        client.close()
        
        return {
            "user": user,
            "session": session,
            "session_token": session_token,
            "test_url": f"http://localhost:5173/?session_token={session_token}&lti=true&subject={test_subject}"
        }
        
    except Exception as e:
        print(f"❌ Error creating session: {e}")
        import traceback
        traceback.print_exc()
        client.close()
        return None

def print_test_instructions(result):
    """Print testing instructions"""
    if not result:
        print("\n❌ Failed to create test session. Check MongoDB connection.")
        return
    
    print("=" * 70)
    print("🎉 TEST SESSION CREATED SUCCESSFULLY!")
    print("=" * 70)
    
    print("\n📋 Test Details:")
    print(f"   User Email: {result['user'].get('email')}")
    print(f"   User ID: {result['user'].get('_id')}")
    print(f"   Session Token: {result['session_token']}")
    print(f"   Subject: {result['session'].get('subject')}")
    print(f"   Course: {result['session'].get('context_label')}")
    
    print("\n🚀 TESTING INSTRUCTIONS:")
    print("\n1. Start the backend (in another terminal):")
    print("   cd app")
    print("   python -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload")
    
    print("\n2. Start the frontend (in another terminal):")
    print("   cd frontend")
    print("   npm run dev")
    
    print("\n3. Open this URL in your browser:")
    print(f"\n   {result['test_url']}")
    
    print("\n✅ Expected Behavior:")
    print("   - Loading spinner appears briefly")
    print("   - Session validates with backend")
    print("   - UI switches to LTI mode (no sidebar)")
    print("   - Context banner shows 'IS-2025-TEST'")
    print("   - User is auto-logged in as test@ugr.es")
    print("   - Subject 'ingenieria_de_servidores' is selected")
    print("   - Chat interface is ready")
    
    print("\n🔍 Verification Steps:")
    print("   1. Check browser DevTools → Console for session logs")
    print("   2. Check Network tab → /session/validate request")
    print("   3. Send a test message")
    print("   4. Check Network tab → /chat request has X-Session-Token header")
    
    print("\n💾 Session Info (for debugging):")
    print(f"   MongoDB Collection: lti_sessions")
    print(f"   Session Document ID: {result['session'].get('_id')}")
    print(f"   Expires: {result['session'].get('expires_at')}")
    
    print("\n" + "=" * 70)

async def main():
    """Main function"""
    print("\n" + "=" * 70)
    print("LTI Session Test Setup - Phase 4 Local Testing")
    print("=" * 70 + "\n")
    
    result = await create_test_session()
    print_test_instructions(result)
    
    if result:
        print("\n✨ You can now test the LTI integration locally!")
        return 0
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
