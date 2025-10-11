# Schema registration moved to apps.py to avoid AppRegistryNotReady errors
from rail_django_graphql.core.registry import schema_registry

# # Open blog schema
schema_registry.register_schema(
    name="blog",
    description="Blog content API",
    settings={
        # "authentication_required": True,
        # "disable_security_mutations": True,
        # "show_metadata": True,
        "schema_settings": {
            "disable_security_mutations": False,
            "show_metadata": True,
        },
        "type_generation_settings": {"exclude_fields": {"Post": ["title"]}},
        "query_settings": {"default_page_size": 20, "max_page_size": 100},
        "mutation_settings": {
            "enable_create": True,
            "generate_update": False,
            "generate_delete": False,
        },
    },
    enabled=True,
)


# # Closed authentication schema
schema_registry.register_schema(
    name="auth",
    description="Authentication and user management",
    models=["auth.User", "auth.Group"],
    exclude_models=["auth.Permission"],  # Exclude specific models
    settings={
        "authentication_required": False,
        "enable_graphiql": True,
        "schema_settings": {
            "disable_security_mutations": False,
        },
    },
    enabled=True,
)

# # Additional open/closed examples
# schema_registry.register_schema(
#     name="public",
#     description="Public data API",
#     models=["public.Resource"],
#     settings={"authentication_required": False, "enable_graphiql": True},
#     enabled=True,
# )

# schema_registry.register_schema(
#     name="private",
#     description="Private data API",
#     models=["private.Document"],
#     settings={"authentication_required": True, "enable_graphiql": False},
#     enabled=True,
# )
# )
