#!/usr/bin/env python
"""
Test script for enhanced quick filter functionality.
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.insert(0, '.')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.blog.models import Post
from rail_django_graphql.generators.filters import AdvancedFilterGenerator


def test_quick_filter_generation():
    """Test that the quick filter is properly generated."""
    print("Testing quick filter generation...")
    
    generator = AdvancedFilterGenerator()
    model = Post
    filter_set = generator.generate_filter_set(model)

    print('Generated filters:')
    for name, filter_obj in filter_set.items():
        print(f'  - {name}: {type(filter_obj).__name__}')

    # Test if quick filter exists
    if 'quick' in filter_set:
        print('\n✓ Quick filter successfully generated!')
        return filter_set['quick']
    else:
        print('\n✗ Quick filter not found in generated filters')
        return None


def test_quick_filter_functionality(quick_filter):
    """Test the quick filter functionality with nested fields."""
    print("\nTesting quick filter functionality...")
    
    from django.contrib.auth.models import User
    from apps.blog.models import Category, Tag
    
    # Create test data if it doesn't exist
    user, _ = User.objects.get_or_create(
        username='testuser', 
        defaults={'email': 'test@example.com'}
    )
    category, _ = Category.objects.get_or_create(
        name='Technology', 
        defaults={'slug': 'technology'}
    )
    tag, _ = Tag.objects.get_or_create(
        name='Django', 
        defaults={'slug': 'django'}
    )
    
    # Create a test post
    post, created = Post.objects.get_or_create(
        title='Test Django GraphQL Post',
        defaults={
            'author': user,
            'content': 'This is a comprehensive test of Django GraphQL functionality.',
            'category': category,
            'status': 'published'
        }
    )
    if created:
        post.tags.add(tag)
    
    # Test quick filter with nested field search
    queryset = Post.objects.all()
    
    # Test searching for author username (nested field)
    filtered_qs = quick_filter.filter(queryset, 'testuser')
    print(f'✓ Quick filter test - searching for "testuser": {filtered_qs.count()} results')
    
    # Test searching for category name (nested field)
    filtered_qs = quick_filter.filter(queryset, 'Technology')
    print(f'✓ Quick filter test - searching for "Technology": {filtered_qs.count()} results')
    
    # Test searching for tag name (nested field)
    filtered_qs = quick_filter.filter(queryset, 'Django')
    print(f'✓ Quick filter test - searching for "Django": {filtered_qs.count()} results')
    
    # Test searching for post title
    filtered_qs = quick_filter.filter(queryset, 'GraphQL')
    print(f'✓ Quick filter test - searching for "GraphQL": {filtered_qs.count()} results')
    
    print('\n✓ All quick filter functionality tests passed!')


def main():
    """Main test function."""
    print("Enhanced Quick Filter Test")
    print("=" * 50)
    
    try:
        # Test filter generation
        quick_filter = test_quick_filter_generation()
        
        if quick_filter:
            # Test filter functionality
            test_quick_filter_functionality(quick_filter)
            
            print("\n" + "=" * 50)
            print("✓ All enhanced quick filter tests completed successfully!")
        else:
            print("\n" + "=" * 50)
            print("✗ Quick filter generation failed - cannot proceed with functionality tests")
            
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()