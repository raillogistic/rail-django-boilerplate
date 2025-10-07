#!/usr/bin/env python
"""
Simple test to verify authentication security fixes.
"""

import requests
import json

def test_authentication():
    """Test authentication with direct HTTP requests."""
    
    print("Testing GraphQL Authentication Security...")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test query
    query = {
        "query": """
        query {
            blog {
                id
                title
                content
            }
        }
        """
    }
    
    # Test 1: No authentication
    print("\n1. Testing without authentication header...")
    try:
        response = requests.post(
            f"{base_url}/graphql/blog/",
            json=query,
            timeout=5
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ PASS: Unauthenticated request blocked")
        else:
            print("❌ FAIL: Unauthenticated request not blocked")
            print(f"Response: {response.text[:200]}")
    except requests.exceptions.ConnectionError:
        print("⚠️  Server not running - start with: python manage.py runserver")
        return
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Test 2: Invalid token
    print("\n2. Testing with invalid token...")
    try:
        response = requests.post(
            f"{base_url}/graphql/blog/",
            json=query,
            headers={"Authorization": "Bearer invalid_token_123"},
            timeout=5
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ PASS: Invalid token blocked")
        else:
            print("❌ FAIL: Invalid token not blocked")
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Random string
    print("\n3. Testing with random string...")
    try:
        response = requests.post(
            f"{base_url}/graphql/blog/",
            json=query,
            headers={"Authorization": "Bearer random_string_should_fail"},
            timeout=5
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ PASS: Random string blocked")
        else:
            print("❌ FAIL: Random string not blocked")
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nTo test with valid authentication:")
    print("1. Start the server: python manage.py runserver")
    print("2. Create a user and get a valid JWT token")
    print("3. Test with: Authorization: Bearer <valid_token>")

if __name__ == '__main__':
    test_authentication()