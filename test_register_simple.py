#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
import json

def test_register():
    client = Client()
    
    # Simple mutation test
    mutation = {
        "query": """
        mutation {
            register(username: "testuser", password: "testpass123", email: "test@example.com") {
                token
                errors
                ok
            }
        }
        """
    }
    
    try:
        response = client.post('/graphql/', 
                             data=json.dumps(mutation),
                             content_type='application/json')
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.content.decode()}")
        
        # Check if user was created
        User = get_user_model()
        user_exists = User.objects.filter(username='testuser').exists()
        print(f"User created: {user_exists}")
        
        if user_exists:
            print("✅ Register mutation working correctly!")
        else:
            print("❌ Register mutation failed to create user")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_register()