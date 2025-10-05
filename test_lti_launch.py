#!/usr/bin/env python3
"""
Test LTI Launch endpoint with mock JWT
"""

import jwt
import requests
from datetime import datetime, timedelta
import json

# Create a mock JWT token
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

print("="*60)
print("Testing LTI Launch Endpoint")
print("="*60)
print()
print(f"Mock JWT Token created for user: {payload['name']}")
print(f"Course: {payload['https://purl.imsglobal.org/spec/lti/claim/context']['title']}")
print()

# Send POST request to /lti/launch
data = {
    "id_token": token,
    "state": "demo-state-123"
}

print("Sending POST request to http://localhost:8080/lti/launch...")
print()

response = requests.post("http://localhost:8080/lti/launch", data=data)

print(f"Response Status: {response.status_code}")
print()

if response.status_code == 200:
    print("✅ Launch successful!")
    print()
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
else:
    print(f"❌ Launch failed with status {response.status_code}")
    print()
    print("Response:")
    print(response.text)

print()
print("="*60)
