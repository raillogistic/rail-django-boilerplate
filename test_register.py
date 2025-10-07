#!/usr/bin/env python
"""
Test script for the register mutation to verify User model import fix.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.test import Client
import json

def test_register_mutation():
    """Test the register mutation with proper GraphQL format."""
    client = Client()
    
    # GraphQL mutation query
    query = """
    mutation {
        register(username: "milia", password: "milia123", email: "milia@example.com") {
            token
            errors
        }
    }
    """
    
    # Send GraphQL request
    response = client.post('/graphql/', 
        data=json.dumps({'query': query}),
        content_type='application/json'
    )
    
    print('Response status:', response.status_code)
    print('Response content:', response.content.decode())
    
    # Parse response
    try:
        response_data = json.loads(response.content.decode())
        if 'errors' in response_data:
            print('GraphQL Errors:', response_data['errors'])
        if 'data' in response_data:
            print('GraphQL Data:', response_data['data'])
    except json.JSONDecodeError as e:
        print('Failed to parse JSON response:', e)

if __name__ == '__main__':
    test_register_mutation()