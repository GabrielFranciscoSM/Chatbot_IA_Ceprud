#!/usr/bin/env python3
"""
Simple script to add sample users to MongoDB using the mongo-service API.

This is an alternative to add_sample_users.py that uses the API instead
of connecting directly to MongoDB.
"""

import requests
import json
from typing import List, Dict

# MongoDB service URL
MONGO_SERVICE_URL = "http://localhost:8081"

# Sample users to add
SAMPLE_USERS = [
    {
        "email": "student1@correo.ugr.es",
        "name": "Juan García López",
        "role": "student",
        "active": True,
        "subjects": ["ingenieria_de_servidores", "modelos_avanzados_computacion"]
    },
    {
        "email": "student2@correo.ugr.es",
        "name": "María Fernández Pérez",
        "role": "student",
        "active": True,
        "subjects": ["metaheuristicas", "estadistica"]
    },
    {
        "email": "student3@correo.ugr.es",
        "name": "Carlos Martínez Ruiz",
        "role": "student",
        "active": True,
        "subjects": ["ingenieria_de_servidores"]
    },
    {
        "email": "teacher1@ugr.es",
        "name": "Dr. Ana Sánchez Torres",
        "role": "teacher",
        "active": True,
        "subjects": ["ingenieria_de_servidores", "modelos_avanzados_computacion", "metaheuristicas"]
    },
    {
        "email": "admin@ugr.es",
        "name": "Administrador CEPRUD",
        "role": "admin",
        "active": True,
        "subjects": []
    }
]


def add_user(user_data: Dict) -> bool:
    """Add a single user via API"""
    try:
        response = requests.post(
            f"{MONGO_SERVICE_URL}/users",
            json=user_data,
            timeout=5
        )
        
        if response.status_code == 200:
            return True
        elif response.status_code == 400:
            # User already exists
            return False
        else:
            print(f"   ⚠️  Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error adding user: {e}")
        return False


def main():
    """Main entry point"""
    print("=" * 60)
    print("  Adding Sample Users via MongoDB Service API")
    print("=" * 60)
    print()
    
    # Check if service is available
    try:
        print(f"Checking MongoDB service at {MONGO_SERVICE_URL}...")
        response = requests.get(f"{MONGO_SERVICE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ MongoDB service is available\n")
        else:
            print(f"❌ MongoDB service returned status {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to MongoDB service: {e}")
        print(f"   Make sure the service is running on {MONGO_SERVICE_URL}")
        return
    
    # Add each user
    added_count = 0
    skipped_count = 0
    error_count = 0
    
    for user_data in SAMPLE_USERS:
        email = user_data["email"]
        name = user_data["name"]
        role = user_data["role"]
        
        print(f"Adding: {name} ({email}) - Role: {role}...", end=" ")
        
        result = add_user(user_data)
        if result is True:
            print("✅ Added")
            added_count += 1
        elif result is False:
            print("⚠️  Already exists")
            skipped_count += 1
        else:
            print("❌ Error")
            error_count += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Summary:")
    print(f"   - Users added: {added_count}")
    print(f"   - Users skipped (already exist): {skipped_count}")
    print(f"   - Errors: {error_count}")
    print(f"{'='*60}\n")
    
    # Try to list all users
    try:
        response = requests.get(f"{MONGO_SERVICE_URL}/users", timeout=5)
        if response.status_code == 200:
            users = response.json()
            print(f"📋 Total users in database: {len(users)}")
            for user in users:
                print(f"   - {user.get('name')} ({user.get('email')}) - {user.get('role')}")
        else:
            print("⚠️  Could not retrieve user list")
    except Exception as e:
        print(f"⚠️  Could not retrieve user list: {e}")


if __name__ == "__main__":
    main()
