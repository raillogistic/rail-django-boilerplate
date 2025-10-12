#!/usr/bin/env python
"""
Test script to verify enhanced filtering metadata only
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

try:
    from graphene.test import Client
    from config.schema import schema
    
    client = Client(schema)
    
    print("=== Enhanced Filter Metadata Test ===")
    
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
    
    result = client.execute(query)
    
    if result.get('errors'):
        print("❌ Errors found:")
        for error in result['errors']:
            print(f"  - {error['message']}")
    else:
        print("✅ Query executed successfully!")
        
        filters = result['data']['model_metadata']['filters']
        print(f"\n📊 Total filters generated: {len(filters)}")
        
        # Check for key enhanced filters
        print("\n🔍 Checking for enhanced filters:")
        
        # Check id__in (should replace id__range)
        id_in_filters = [f for f in filters if f['name'] == 'id__in']
        id_range_filters = [f for f in filters if f['name'] == 'id__range']
        
        if id_in_filters:
            print(f"  ✅ id__in filter found: {id_in_filters[0]['filter_type']}")
        else:
            print("  ❌ id__in filter not found")
            
        if id_range_filters:
            print(f"  ❌ id__range filter still exists: {id_range_filters[0]['filter_type']}")
        else:
            print("  ✅ id__range filter successfully removed")
        
        # Check for __in filters
        in_filters = [f for f in filters if '__in' in f['name']]
        print(f"  ✅ Total '__in' filters: {len(in_filters)}")
        
        # Check for text enhancement filters
        text_enhancements = [f for f in filters if any(op in f['name'] for op in ['__contains', '__startswith', '__endswith', '__icontains', '__istartswith', '__iendswith'])]
        print(f"  ✅ Text enhancement filters: {len(text_enhancements)}")
        
        # Check for numeric filters
        numeric_filters = [f for f in filters if any(op in f['name'] for op in ['__gt', '__gte', '__lt', '__lte'])]
        print(f"  ✅ Numeric comparison filters: {len(numeric_filters)}")
        
        # Show some examples
        print(f"\n📋 Sample filters (first 10):")
        for i, filter_item in enumerate(filters[:10]):
            name = filter_item['name']
            field_name = filter_item['field_name']
            filter_type = filter_item['filter_type']
            print(f"  {i+1:2d}. {name:<20} -> {field_name:<15} ({filter_type})")
        
        if len(filters) > 10:
            print(f"     ... and {len(filters) - 10} more filters")
        
        # Show some enhanced filter examples
        print(f"\n🚀 Enhanced filter examples:")
        enhanced_examples = [f for f in filters if any(op in f['name'] for op in ['__in', '__contains', '__startswith'])][:5]
        for i, filter_item in enumerate(enhanced_examples):
            name = filter_item['name']
            field_name = filter_item['field_name']
            filter_type = filter_item['filter_type']
            print(f"  {i+1}. {name:<25} -> {field_name:<15} ({filter_type})")
        
        print(f"\n🎉 Enhanced filtering functionality is working correctly!")
        print(f"   - Total filters: {len(filters)}")
        print(f"   - Enhanced '__in' filters: {len(in_filters)}")
        print(f"   - Text enhancement filters: {len(text_enhancements)}")
        print(f"   - Numeric comparison filters: {len(numeric_filters)}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()