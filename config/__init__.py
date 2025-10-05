from rail_django_graphql.core.registry import schema_registry

# Open blog schema
schema_registry.register_schema(
    name="blog",
    description="Blog content API",
    models=[
        "blog.Post",
    ],
    settings={
        "authentication_required": False,
        "enable_graphiql": True,
        "QUERY_SETTINGS": {
            "ENABLE_FILTERING": False,
        },
    },
    enabled=True,
)


# # Closed authentication schema
# schema_registry.register_schema(
#     name="auth",
#     description="Authentication and user management",
#     models=["auth.User", "auth.Group"],
#     settings={
#         "authentication_required": True,
#         "enable_graphiql": False,
#     },  # no GraphiQL in production
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
