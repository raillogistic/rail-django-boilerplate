#!/usr/bin/env python
"""
Test script to verify schema registration parameters are working correctly.
"""
import os
import sys
import django

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from config import schema_registry
from django.apps import apps

def test_schema_registration():
    """Test that schema registration parameters are working correctly."""
    print("Testing schema registration parameters...")
    
    # Get the blog schema info
    blog_schema = schema_registry.get_schema('blog')
    print(f"SchemaInfo:")
    print(f"  name: {blog_schema.name}")
    print(f"  apps: {blog_schema.apps}")
    print(f"  models: {blog_schema.models}")
    print(f"  exclude_models: {blog_schema.exclude_models}")
    print(f"  enabled: {blog_schema.enabled}")
    
    # Debug: Check what models are available in the blog app
    print("\nDebugging app models...")
    from django.apps import apps
    try:
        blog_app = apps.get_app_config('blog')
        all_blog_models = blog_app.get_models()
        print(f"All models in blog app: {[m.__name__ for m in all_blog_models]}")
        print(f"Model full names: {[f'{m._meta.app_label}.{m._meta.model_name}' for m in all_blog_models]}")
    except LookupError as e:
        print(f"Error getting blog app: {e}")
    
    # Test model discovery
    print("\nTesting model discovery...")
    models = schema_registry.get_models_for_schema('blog')
    discovered_models = [f"{model._meta.app_label}.{model._meta.model_name}" for model in models]
    print(f"Discovered models: {discovered_models}")
    
    # Check if the parameters are working as expected
    print("\nValidation:")
    
    # Check if only blog app models are included
    blog_models = [m for m in discovered_models if m.startswith('blog.')]
    non_blog_models = [m for m in discovered_models if not m.startswith('blog.')]
    
    print(f"Blog models found: {blog_models}")
    print(f"Non-blog models found: {non_blog_models}")
    
    # Check if Comment model is excluded
    comment_included = 'blog.comment' in discovered_models
    print(f"Comment model excluded: {not comment_included}")
    
    # Check if Post model is included
    post_included = 'blog.post' in discovered_models
    print(f"Post model included: {post_included}")
    
    return {
        'schema_info': blog_schema,
        'discovered_models': discovered_models,
        'comment_excluded': not comment_included,
        'post_included': post_included
    }

if __name__ == "__main__":
    results = test_schema_registration()