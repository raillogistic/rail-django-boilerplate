"""
Development settings for django-graphql-boilerplate project (env-driven).
"""

import environ

from .base import *

env = environ.Env()

# Development toggles
DEBUG = env.bool("DJANGO_DEBUG", default=True)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# GraphiQL and introspection (development overrides)
RAIL_DJANGO_GRAPHQL["ENABLE_GRAPHIQL"] = env.bool(
    "ENABLE_GRAPHIQL", default=True
)
RAIL_DJANGO_GRAPHQL["ENABLE_INTROSPECTION"] = env.bool(
    "ENABLE_INTROSPECTION", default=True
)

# Override schema-specific settings for development
RAIL_DJANGO_GRAPHQL["SCHEMAS"]["default"]["SCHEMA_SETTINGS"]["enable_graphiql"] = env.bool(
    "ENABLE_GRAPHIQL", default=True
)
RAIL_DJANGO_GRAPHQL["SCHEMAS"]["default"]["SCHEMA_SETTINGS"]["enable_introspection"] = env.bool(
    "ENABLE_INTROSPECTION", default=True
)

# Email backend for development
EMAIL_BACKEND = env(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
