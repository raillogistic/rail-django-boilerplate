#!/usr/bin/env python
"""
Debug script to test SchemaBuilder initialization and registry integration.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from rail_django_graphql.core.registry import schema_registry
from rail_django_graphql.core.schema import SchemaBuilder

def main():
    print("=== Debug SchemaBuilder Initialization ===")
    
    # Create a builder and check its properties step by step
    print('Creating SchemaBuilder with schema_name="blog"')
    builder = SchemaBuilder(schema_name='blog', registry=schema_registry)

    print('After initialization:')
    print(f'  schema_name: {repr(builder.schema_name)}')
    print(f'  registry: {builder.registry is not None}')

    # Check if the schema is registered in the registry
    print('\nChecking registry:')
    schemas = schema_registry.list_schemas()
    print(f'  Registered schemas: {[s.name for s in schemas]}')

    # Check if the blog schema exists
    blog_schema = schema_registry.get_schema('blog')
    print(f'  Blog schema exists: {blog_schema is not None}')
    if blog_schema:
        print(f'  Blog schema info: {blog_schema}')
    
    # Test model discovery
    print('\n=== Testing Model Discovery ===')
    print('Registry models for blog schema:')
    models = schema_registry.get_models_for_schema('blog')
    print(f'  Models: {[m.__name__ for m in models]}')

    print('\nSchema builder discovered models:')
    discovered = builder._discover_models()
    print(f'  Discovered: {[m.__name__ for m in discovered]}')
    
    # Test the condition in _discover_models
    print('\n=== Testing Discovery Condition ===')
    print(f'  builder.registry: {builder.registry is not None}')
    print(f'  builder.schema_name: {repr(builder.schema_name)}')
    print(f'  schema_name != "default": {builder.schema_name != "default"}')
    
    condition_passes = builder.registry and builder.schema_name != "default"
    print(f'  Condition passes: {condition_passes}')
    
    if condition_passes:
        try:
            registry_models = builder.registry.get_models_for_schema(builder.schema_name)
            print(f'  Registry returned {len(registry_models)} models')
            print(f'  Registry models truthy: {bool(registry_models)}')
        except Exception as e:
            print(f'  Exception: {e}')

if __name__ == '__main__':
    main()