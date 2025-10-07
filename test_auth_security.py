#!/usr/bin/env python
"""
Test script to verify authentication security fixes.
Tests that authentication_required properly blocks unauthorized requests.
"""

import os
import sys
import django
from django.conf import settings

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Setup Django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
import json

def test_authentication_security():
    """Test that authentication_required properly blocks unauthorized requests."""
    
    print("Testing GraphQL Authentication Security...")
    print("=" * 50)
    
    client = Client()
    User = get_user_model()
    
    # Test 1: Unauthenticated request should be blocked
    print("\n1. Testing unauthenticated request (should be blocked)...")
    
    query = """
    query {
        blog {
            id
            title
            content
        }
    }
    """
    
    response = client.post(
        '/graphql/blog/',
        {
            'query': query
        },
        content_type='application/json'
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 401:
        print("✅ PASS: Unauthenticated request properly blocked")
    else:
        print("❌ FAIL: Unauthenticated request was not blocked")
        try:
            response_data = json.loads(response.content)
            print(f"Response: {response_data}")
        except:
            print(f"Raw response: {response.content}")
    
    # Test 2: Invalid token should be blocked
    print("\n2. Testing invalid token (should be blocked)...")
    
    response = client.post(
        '/graphql/blog/',
        {
            'query': query
        },
        content_type='application/json',
        HTTP_AUTHORIZATION='Bearer invalid_token_123'
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 401:
        print("✅ PASS: Invalid token properly blocked")
    else:
        print("❌ FAIL: Invalid token was not blocked")
        try:
            response_data = json.loads(response.content)
            print(f"Response: {response_data}")
        except:
            print(f"Raw response: {response.content}")
    
    # Test 3: Random string as token should be blocked
    print("\n3. Testing random string as token (should be blocked)...")
    
    response = client.post(
        '/graphql/blog/',
        {
            'query': query
        },
        content_type='application/json',
        HTTP_AUTHORIZATION='Bearer random_string_that_should_fail'
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 401:
        print("✅ PASS: Random string token properly blocked")
    else:
        print("❌ FAIL: Random string token was not blocked")
        try:
            response_data = json.loads(response.content)
            print(f"Response: {response_data}")
        except:
            print(f"Raw response: {response.content}")
    
    # Test 4: Create a valid user and token for positive test
    print("\n4. Testing with valid authentication...")
    
    try:
        # Create test user
        user = User.objects.create_user(
            username='testuser_auth',
            email='test@example.com',
            password='testpass123'
        )
        
        # Generate valid JWT token
        from rail_django_graphql.extensions.auth import JWTManager
        token = JWTManager.generate_token(user)
        
        response = client.post(
            '/graphql/blog/',
            {
                'query': query
            },
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ PASS: Valid token properly accepted")
        else:
            print("❌ FAIL: Valid token was rejected")
            try:
                response_data = json.loads(response.content)
                print(f"Response: {response_data}")
            except:
                print(f"Raw response: {response.content}")
        
        # Cleanup
        user.delete()
        
    except Exception as e:
        print(f"❌ Error testing valid authentication: {e}")
    
    print("\n" + "=" * 50)
    print("Authentication security test completed!")

if __name__ == '__main__':
    test_authentication_security()