#!/usr/bin/env python3
"""
Test script to query filter metadata from GraphQL endpoint.

This script validates that the filters field in ModelMetadataType
correctly returns filter metadata matching the AdvancedFilterGenerator.
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

def query_filter_metadata():
    """Query filter metadata for blog.Post model."""
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
    
    # GraphQL query to fetch model metadata with filters
    query = """
    query GetModelMetadataWithFilters($appName: String!, $modelName: String!) {
        model_metadata(app_name: $appName, model_name: $modelName) {
            app_name
            model_name
            verbose_name
            filters {
                name
                field_name
                filter_type
                lookup_expr
                help_text
                is_nested
                related_model
            }
        }
    }
    """
    
    # Variables for the query
    variables = {
        "appName": "blog",
        "modelName": "Post"
    }
    
    # Request payload
    payload = {
        'query': query,
        'variables': variables
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'errors' in result:
                print("GraphQL Errors:")
                for error in result['errors']:
                    print(f"  - {error.get('message', 'Unknown error')}")
            else:
                print("Filter Metadata Query Successful!")
                metadata = result.get('data', {}).get('model_metadata')
                if metadata:
                    print(f"Model: {metadata['app_name']}.{metadata['model_name']}")
                    print(f"Verbose Name: {metadata['verbose_name']}")
                    print(f"Number of filters: {len(metadata['filters'])}")
                    print("\nFilter Details:")
                    for filter_info in metadata['filters']:
                        print(f"  - {filter_info['name']}")
                        print(f"    Field: {filter_info['field_name']}")
                        print(f"    Type: {filter_info['filter_type']}")
                        if filter_info['lookup_expr']:
                            print(f"    Lookup: {filter_info['lookup_expr']}")
                        if filter_info['is_nested']:
                            print(f"    Nested: {filter_info['related_model']}")
                        if filter_info['help_text']:
                            print(f"    Help: {filter_info['help_text']}")
                        print()
                else:
                    print("No metadata returned")
        else:
            print(f"HTTP Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    query_filter_metadata()