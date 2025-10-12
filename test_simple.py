#!/usr/bin/env python3
"""
Simple test script to validate the filters field in ModelMetadataType.
"""

import json
import requests

def test_simple():
    """Simple test."""
    
    # GraphQL endpoint
    url = "http://127.0.0.1:8000/graphql/"
    
    # Headers
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Simple query
    query = """
    query {
        model_metadata(app_name: "blog", model_name: "Post") {
            model_name
            app_name
            filters {
                name
                filter_type
            }
        }
    }
    """
    
    try:
        response = requests.post(url, json={'query': query}, headers=headers)
        print(f"Status: {response.status_code}")
        data = response.json()
        print("Response:", json.dumps(data, indent=2))
        
        if data.get('data', {}).get('model_metadata'):
            metadata = data['data']['model_metadata']
            filters = metadata.get('filters', [])
            print(f"Found {len(filters)} filters")
        else:
            print("No metadata")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_simple()