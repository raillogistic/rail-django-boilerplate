#!/usr/bin/env python
"""
Test script to verify the complete fix for blog schema mutation settings
"""

import os
import sys

import django

# Add the rail-django-graphql package to the path
sys.path.insert(0, os.path.join(os.path.dirname(os.getcwd()), "rail-django-graphql"))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_graphql_boilerplate.settings")
django.setup()

from django.conf import settings
from rail_django_graphql.conf import SettingsProxy, get_mutation_generator_settings
from rail_django_graphql.core.registry import register_schema, schema_registry
from rail_django_graphql.core.schema import SchemaBuilder
from rail_django_graphql.generators.mutations import MutationGenerator
from rail_django_graphql.generators.types import TypeGenerator

print("=== Test Final Fix for Blog Schema Mutation Settings ===")

# 0. Register blog schema with custom settings first
print("0. Registering blog schema with custom mutation settings...")
register_schema(
    "blog",
    apps=["blog"],
    models=["blog.Post", "blog.Comment"],
    settings={
        "mutation_settings": {
            "enable_create": False,
            "generate_update": False,
            "generate_delete": False,
        }
    },
)
print("   ✅ Blog schema registered")
print()

# 1. Check Django settings state
print("1. Django settings state:")
rail_schemas = getattr(settings, "RAIL_DJANGO_GRAPHQL_SCHEMAS", "NOT_SET")
if rail_schemas != "NOT_SET" and "blog" in rail_schemas:
    print(f"   Blog schema found in Django settings")
    print(f"   Blog settings: {rail_schemas['blog']}")
    if "mutation_settings" in rail_schemas["blog"]:
        print(f"   Blog mutation_settings: {rail_schemas['blog']['mutation_settings']}")
else:
    print(f"   Blog schema NOT found in Django settings")
    print(f"   RAIL_DJANGO_GRAPHQL_SCHEMAS: {rail_schemas}")
print()

# 2. Test SettingsProxy
print("2. SettingsProxy for blog schema:")
try:
    proxy = SettingsProxy("blog")
    mutation_settings = proxy.get("mutation_settings", {})
    print(f"   mutation_settings from proxy: {mutation_settings}")
    print(f"   Type: {type(mutation_settings)}")

    # Check specific settings
    if mutation_settings:
        print(f"   enable_create: {mutation_settings.get('enable_create', 'NOT_SET')}")
        print(
            f"   generate_update: {mutation_settings.get('generate_update', 'NOT_SET')}"
        )
        print(
            f"   generate_delete: {mutation_settings.get('generate_delete', 'NOT_SET')}"
        )

except Exception as e:
    print(f"   ERROR: {e}")
    import traceback

    traceback.print_exc()
print()

# 3. Test get_mutation_generator_settings
print("3. get_mutation_generator_settings('blog'):")
try:
    generator_settings = get_mutation_generator_settings("blog")
    print(f"   Result: {generator_settings}")
    print(f"   Type: {type(generator_settings)}")

    # Check specific settings that should be False
    print(f"   enable_create: {generator_settings.enable_create} (expected: False)")
    print(f"   generate_update: {generator_settings.generate_update} (expected: False)")
    print(f"   generate_delete: {generator_settings.generate_delete} (expected: False)")

    # Verify expected values
    if generator_settings.enable_create == False:
        print("   ✅ enable_create correctly set to False")
    else:
        print("   ❌ enable_create not set correctly")

    if generator_settings.generate_update == False:
        print("   ✅ generate_update correctly set to False")
    else:
        print("   ❌ generate_update not set correctly")

    if generator_settings.generate_delete == False:
        print("   ✅ generate_delete correctly set to False")
    else:
        print("   ❌ generate_delete not set correctly")

except Exception as e:
    print(f"   ERROR: {e}")
    import traceback

    traceback.print_exc()
print()

# 4. Test MutationGenerator initialization
print("4. MutationGenerator initialization for blog schema:")
try:
    # Create a TypeGenerator (needed for MutationGenerator)
    type_generator = TypeGenerator(schema_name="blog")

    # Test MutationGenerator with None settings (should use hierarchical settings)
    mutation_generator = MutationGenerator(type_generator, schema_name="blog")

    print(f"   MutationGenerator created: {type(mutation_generator)}")
    print(f"   Schema name: {mutation_generator.schema_name}")
    print(f"   Settings: {mutation_generator.settings}")
    print(
        f"   enable_create: {mutation_generator.settings.enable_create} (expected: False)"
    )
    print(
        f"   generate_update: {mutation_generator.settings.generate_update} (expected: False)"
    )
    print(
        f"   generate_delete: {mutation_generator.settings.generate_delete} (expected: False)"
    )

    # Verify expected values
    if mutation_generator.settings.enable_create == False:
        print("   ✅ MutationGenerator enable_create correctly set to False")
    else:
        print("   ❌ MutationGenerator enable_create not set correctly")

    if mutation_generator.settings.generate_update == False:
        print("   ✅ MutationGenerator generate_update correctly set to False")
    else:
        print("   ❌ MutationGenerator generate_update not set correctly")

    if mutation_generator.settings.generate_delete == False:
        print("   ✅ MutationGenerator generate_delete correctly set to False")
    else:
        print("   ❌ MutationGenerator generate_delete not set correctly")

except Exception as e:
    print(f"   ERROR: {e}")
    import traceback

    traceback.print_exc()
print()

# 5. Test SchemaBuilder's mutation_generator
print("5. Schema builder's mutation_generator for blog schema:")
try:
    schema_builder = SchemaBuilder(schema_name="blog")
    print(f"   Schema builder created: {type(schema_builder)}")

    mutation_gen_from_builder = schema_builder.mutation_generator
    print(f"   Mutation generator: {type(mutation_gen_from_builder)}")
    print(f"   Schema name: {mutation_gen_from_builder.schema_name}")
    print(f"   Settings: {mutation_gen_from_builder.settings}")
    print(
        f"   enable_create: {mutation_gen_from_builder.settings.enable_create} (expected: False)"
    )
    print(
        f"   generate_update: {mutation_gen_from_builder.settings.generate_update} (expected: False)"
    )
    print(
        f"   generate_delete: {mutation_gen_from_builder.settings.generate_delete} (expected: False)"
    )

    # Verify expected values
    if mutation_gen_from_builder.settings.enable_create == False:
        print(
            "   ✅ Schema builder MutationGenerator enable_create correctly set to False"
        )
    else:
        print("   ❌ Schema builder MutationGenerator enable_create not set correctly")

    if mutation_gen_from_builder.settings.generate_update == False:
        print(
            "   ✅ Schema builder MutationGenerator generate_update correctly set to False"
        )
    else:
        print(
            "   ❌ Schema builder MutationGenerator generate_update not set correctly"
        )

    if mutation_gen_from_builder.settings.generate_delete == False:
        print(
            "   ✅ Schema builder MutationGenerator generate_delete correctly set to False"
        )
    else:
        print(
            "   ❌ Schema builder MutationGenerator generate_delete not set correctly"
        )

except Exception as e:
    print(f"   ERROR: {e}")
    import traceback

    traceback.print_exc()
print()

print("=== Test Complete ===")
print("If all checks show ✅, the fix is working correctly!")
