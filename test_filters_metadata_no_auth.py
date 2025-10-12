#!/usr/bin/env python3
"""
Test script to validate the filters field in ModelMetadataType without authentication.
"""

import json
import requests

def test_filters_metadata():
    """Test the filters field in model metadata."""
    
    # GraphQL endpoint
    url = "http://127.0.0.1:8000/graphql/"
    
    # Headers without authentication
    headers = {
        'Content-Type': 'application/json'
    }
    
    # GraphQL query to test filters metadata
    query = """
    query TestFiltersMetadata {
        model_metadata(app_name: "blog", model_name: "Post") {
            model_name
            app_name
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
    
    # Make the request
    try:
        response = requests.post(url, json={'query': query}, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Response:")
            print(json.dumps(data, indent=2))
            
            # Check if we got metadata
            if data.get('data', {}).get('model_metadata'):
                metadata = data['data']['model_metadata']
                print(f"\n✅ Successfully retrieved metadata for {metadata['app_name']}.{metadata['model_name']}")
                
                # Check filters
                filters = metadata.get('filters', [])
                if filters:
                    print(f"✅ Found {len(filters)} filters:")
                    for filter_item in filters[:10]:  # Show first 10 filters
                        print(f"  - {filter_item['name']}: {filter_item['filter_type']} ({filter_item['lookup_expr']})")
                    if len(filters) > 10:
                        print(f"  ... and {len(filters) - 10} more filters")
                else:
                    print("❌ No filters found in metadata")
            else:
                print("❌ No metadata returned")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print("Response:", response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_filters_metadata()