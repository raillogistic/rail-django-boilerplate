#!/usr/bin/env python
"""
Test script for enhanced filtering functionality
"""
import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from graphene.test import Client
from config.schema import schema

def test_enhanced_filters():
    """Test the enhanced filtering functionality"""
    client = Client(schema)
    
    # Test the model_metadata query to see the new grouped filters
    query = """
    query {
      model_metadata(app_name: "blog", model_name: "Post") {
        model_name
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
    
    print("Testing enhanced filter metadata...")
    result = client.execute(query)
    
    if result.get('errors'):
        print("Status: Error")
        print("Errors:", json.dumps(result['errors'], indent=2))
    else:
        print("Status: 200")
        print("Result:", json.dumps(result, indent=2))
        
        # Count filters and operations
        if result.get('data') and result['data'].get('model_metadata'):
            filters = result['data']['model_metadata'].get('filters', [])
            print(f"\nTotal filters: {len(filters)}")
            
            # Show first few filters as examples
            for i, filter_item in enumerate(filters[:10]):
                print(f"Filter {i+1}: '{filter_item['name']}' -> field '{filter_item.get('field_name', 'N/A')}' (type: {filter_item.get('filter_type', 'N/A')})")
            
            if len(filters) > 10:
                print(f"... and {len(filters) - 10} more filters")

if __name__ == "__main__":
    test_enhanced_filters()