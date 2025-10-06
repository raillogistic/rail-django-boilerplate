# Schema registration moved to apps.py to avoid AppRegistryNotReady errors
# from rail_django_graphql.core.registry import schema_registry

# # Open blog schema
# schema_registry.register_schema(
#     name="blog",
#     description="Blog content API",
#     # models=[
#     #     "blog.Post",
#     # ],
#     # apps=["blog"],
#     settings={
#         "MUTATION_SETTINGS": {
#             "generate_create": True,  # Enable create mutations
#             "generate_update": True,  # Enable update mutations
#             "generate_delete": False,  # Disable delete mutations
#             "enable_method_mutations": False,  # Disable method-based mutations
#             "generate_bulk": False,  # Disable bulk operations
#         }
#     },
#     enabled=True,
# )


# # Closed authentication schema
# schema_registry.register_schema(
#     name="auth",
#     description="Authentication and user management",
#     models=["auth.User", "auth.Group"],
#     exclude_models=["auth.Permission"],  # Exclude specific models
#     settings={
#         "authentication_required": False,
#         "enable_graphiql": True,
#         "DISABLE_SECURITY_MUTATIONS": True,
#     },
#     enabled=True,
# )

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
