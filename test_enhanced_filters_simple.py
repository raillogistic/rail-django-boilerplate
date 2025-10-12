#!/usr/bin/env python
"""
Simple test script for enhanced filtering functionality
"""
import os
import django
import json
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

try:
    from graphene.test import Client
    from config.schema import schema
    
    client = Client(schema)
    
    # Test the model_metadata query
    query = """
    query {
      model_metadata(app_name: "blog", model_name: "Post") {
        model_name
        filters {
          name
          field_name
          filter_type
        }
      }
    }
    """
    
    print("Testing enhanced filter metadata...")
    result = client.execute(query)
    
    if result.get('errors'):
        print("Status: Error")
        for error in result['errors']:
            print(f"Error: {error['message']}")
    else:
        print("Status: 200 - Success!")
        data = result.get('data', {})
        model_metadata = data.get('model_metadata', {})
        filters = model_metadata.get('filters', [])
        
        print(f"Model: {model_metadata.get('model_name', 'Unknown')}")
        print(f"Total filters: {len(filters)}")
        
        # Show some example filters
        for i, filter_item in enumerate(filters[:5]):
            name = filter_item.get('name', 'N/A')
            field_name = filter_item.get('field_name', 'N/A')
            filter_type = filter_item.get('filter_type', 'N/A')
            print(f"  {i+1}. {name} -> {field_name} ({filter_type})")
        
        if len(filters) > 5:
            print(f"  ... and {len(filters) - 5} more filters")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()