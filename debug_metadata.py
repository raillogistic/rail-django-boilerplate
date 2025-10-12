#!/usr/bin/env python3
"""
Debug script to test metadata query directly and identify issues.
"""

import json
import os
import sys
import requests

def load_jwt_token():
    """Load JWT token from jwt.json file."""
    jwt_path = os.path.join(os.path.dirname(__file__), 'jwt.json')
    try:
        with open(jwt_path, 'r') as f:
            data = json.load(f)
            return data.get('token')
    except FileNotFoundError:
        print(f"JWT file not found at {jwt_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JWT file: {e}")
        return None

def debug_metadata_query():
    """Debug the metadata query step by step."""
    token = load_jwt_token()
    if not token:
        print("No JWT token available")
        return
    
    # GraphQL endpoint
    url = "http://127.0.0.1:8000/graphql/"
    
    # Headers with Bearer token
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Simple query first
    simple_query = """
    query {
        model_metadata(app_name: "blog", model_name: "Post") {
            app_name
            model_name
        }
    }
    """
    
    print("Testing simple metadata query...")
    payload = {'query': simple_query}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Response:", json.dumps(result, indent=2))
        else:
            print(f"HTTP Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    debug_metadata_query()