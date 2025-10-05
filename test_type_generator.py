#!/usr/bin/env python
"""
Test script to debug TypeGenerator issue with blog schema
"""

import os
import sys

import django

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from apps.blog.models import Comment, Post
from rail_django_graphql.conf import get_type_generation_settings
from rail_django_graphql.generators.types import TypeGenerator


def test_type_generator():
    print("Testing TypeGenerator with blog schema...")

    # Test 1: Check if settings are loaded correctly
    print("\n1. Testing settings loading:")
    settings = get_type_generation_settings("blog")
    print(f"Settings type: {type(settings)}")
    print(f"Settings content: {settings}")

    # Test 2: Create TypeGenerator instance
    print("\n2. Creating TypeGenerator instance:")
    try:
        type_generator = TypeGenerator(schema_name="blog")
        print(f"TypeGenerator created successfully")
        print(f"TypeGenerator settings: {type_generator.settings}")
        print(f"TypeGenerator settings type: {type(type_generator.settings)}")
    except Exception as e:
        print(f"Error creating TypeGenerator: {e}")
        import traceback

        traceback.print_exc()
        return

    # Test 3: Generate object type for Post model
    print("\n3. Testing object type generation for Post model:")
    try:
        post_type = type_generator.generate_object_type(Post)
        print(f"Post type generated: {post_type}")
        print(f"Post type name: {post_type.__name__}")
        print(
            f"Post type fields: {list(post_type._meta.fields.keys()) if hasattr(post_type._meta, 'fields') else 'No fields found'}"
        )
    except Exception as e:
        print(f"Error generating Post type: {e}")
        import traceback

        traceback.print_exc()

    # Test 4: Generate object type for Comment model
    print("\n4. Testing object type generation for Comment model:")
    try:
        comment_type = type_generator.generate_object_type(Comment)
        print(f"Comment type generated: {comment_type}")
        print(f"Comment type name: {comment_type.__name__}")
        print(
            f"Comment type fields: {list(comment_type._meta.fields.keys()) if hasattr(comment_type._meta, 'fields') else 'No fields found'}"
        )
    except Exception as e:
        print(f"Error generating Comment type: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_type_generator()
