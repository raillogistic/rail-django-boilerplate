#!/usr/bin/env python
"""
Test script for reverse field filtering functionality.

This script tests the AdvancedFilterGenerator's ability to create filters
for reverse relationship fields using the actual blog models.
"""

import os
import sys
import django

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Add the rail_django_graphql package to the path
# rail_graphql_path = os.path.join(project_root, '..', 'rail-django-graphql')
# sys.path.insert(0, rail_graphql_path)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

# Import Django models and the filter generator
from django.contrib.auth import get_user_model
from apps.blog.models import Post, Comment, Category, Tag
from rail_django_graphql.generators.filters import AdvancedFilterGenerator

User = get_user_model()


def test_reverse_field_filters():
    """
    Test the reverse field filtering functionality using actual blog models.
    
    This function tests that the AdvancedFilterGenerator correctly generates
    filters for reverse relationship fields.
    """
    print("Testing reverse field filtering functionality with blog models...")
    
    # Initialize the filter generator
    filter_generator = AdvancedFilterGenerator()
    
    # Test with User model (should have reverse filters for posts and comments)
    print("\n1. Testing User model filters:")
    try:
        # First, let's debug what reverse relationships are found
        print("   Debugging reverse relationships:")
        all_fields = User._meta.get_fields()
        print(f"   All fields: {[f.name for f in all_fields]}")
        
        reverse_relations = [
            field for field in all_fields
            if field.is_relation and (field.one_to_many or field.one_to_one)
        ]
        print(f"   Found {len(reverse_relations)} reverse relationships:")
        for rel in reverse_relations:
            print(f"     - {rel.name} (type: {type(rel).__name__}, one_to_many: {getattr(rel, 'one_to_many', False)}, one_to_one: {getattr(rel, 'one_to_one', False)})")
            if hasattr(rel, 'related_model'):
                print(f"       -> {rel.related_model.__name__}")
                print(f"       -> accessor: {rel.get_accessor_name()}")
        
        user_filter_set = filter_generator.generate_filter_set(User)
        user_filters = list(user_filter_set.base_filters.keys())
        
        print(f"   Total filters generated: {len(user_filters)}")
        
        # Show first 20 filters to debug
        print("   Sample filters:")
        for i, filter_name in enumerate(sorted(user_filters)):
            if i < 20:  # Show first 20
                print(f"     - {filter_name}")
            elif i == 20:
                print(f"     ... and {len(user_filters) - 20} more")
                break
        
        # Look for reverse field filters
        reverse_filters = [f for f in user_filters if 'posts__' in f or 'comments__' in f]
        print(f"   Reverse field filters found: {len(reverse_filters)}")
        
        if reverse_filters:
            print("   Sample reverse field filters:")
            for filter_name in reverse_filters[:10]:  # Show first 10
                print(f"     - {filter_name}")
        else:
            print("   No reverse field filters found")
            
        # Look for specific expected filters
        expected_filters = [
            'posts__title',
            'posts__title__contains',
            'posts__content',
            'posts__created_at',
            'comments__content',
            'comments__created_at',
        ]
        
        found_expected = [f for f in expected_filters if f in user_filters]
        print(f"   Expected reverse filters found: {len(found_expected)}/{len(expected_filters)}")
        
        if found_expected:
            print("   Found expected filters:")
            for filter_name in found_expected:
                print(f"     ✓ {filter_name}")
        
        missing_expected = [f for f in expected_filters if f not in user_filters]
        if missing_expected:
            print("   Missing expected filters:")
            for filter_name in missing_expected:
                print(f"     ✗ {filter_name}")
                
    except Exception as e:
        print(f"   Error testing User filters: {e}")
        import traceback
        traceback.print_exc()
    
    # Test with Post model (should have reverse filters for comments)
    print("\n2. Testing Post model filters:")
    try:
        # Debug reverse relationships for Post
        print("   Debugging reverse relationships:")
        all_fields = Post._meta.get_fields()
        print(f"   All fields: {[f.name for f in all_fields]}")
        
        reverse_relations = [
            field for field in all_fields
            if field.is_relation and (field.one_to_many or field.one_to_one)
        ]
        print(f"   Found {len(reverse_relations)} reverse relationships:")
        for rel in reverse_relations:
            print(f"     - {rel.name} (type: {type(rel).__name__}, one_to_many: {getattr(rel, 'one_to_many', False)}, one_to_one: {getattr(rel, 'one_to_one', False)})")
            if hasattr(rel, 'related_model'):
                print(f"       -> {rel.related_model.__name__}")
                print(f"       -> accessor: {rel.get_accessor_name()}")
        
        post_filter_set = filter_generator.generate_filter_set(Post)
        post_filters = list(post_filter_set.base_filters.keys())
        
        print(f"   Total filters generated: {len(post_filters)}")
        
        # Look for reverse field filters
        reverse_filters = [f for f in post_filters if 'comments__' in f]
        print(f"   Reverse field filters found: {len(reverse_filters)}")
        
        if reverse_filters:
            print("   Sample reverse field filters:")
            for filter_name in reverse_filters[:10]:  # Show first 10
                print(f"     - {filter_name}")
        else:
            print("   No reverse field filters found")
            
    except Exception as e:
        print(f"   Error testing Post filters: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nReverse field filtering test completed!")


if __name__ == "__main__":
    test_reverse_field_filters()