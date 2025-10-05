"""
Base settings for django-graphql-boilerplate project (env-driven).
"""

import os
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# django-environ setup
env = environ.Env()
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
if ENVIRONMENT.lower() == "development":
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        environ.Env.read_env(str(env_file))

"""Core Django settings via environment"""
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-change-me-in-production")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DJANGO_DEBUG", default=False)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])

LANGUAGE_CODE = env("DJANGO_LANGUAGE_CODE", default="en-us")
TIME_ZONE = env("DJANGO_TIME_ZONE", default="UTC")

# Security and CSRF
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
SECURE_PROXY_SSL_HEADER = env("SECURE_PROXY_SSL_HEADER", default=None)
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=False)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=False)

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "graphene_django",
    "corsheaders",
    "rail_django_graphql",
]

LOCAL_APPS = [
    "apps.core",
    "apps.users",
    "apps.blog",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

"""Database configuration via DATABASE_URL"""
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

USE_I18N = True
USE_TZ = True

"""Static and media paths via environment"""
STATIC_URL = env("STATIC_URL", default="/static/")
STATIC_ROOT = Path(env("STATIC_ROOT", default=str(BASE_DIR / "staticfiles")))
_project_static = BASE_DIR / "static"
STATICFILES_DIRS = [_project_static] if _project_static.exists() else []

MEDIA_URL = env("MEDIA_URL", default="/media/")
MEDIA_ROOT = Path(env("MEDIA_ROOT", default=str(BASE_DIR / "media")))

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom user model
AUTH_USER_MODEL = "users.User"

# GraphQL Configuration
GRAPHENE = {
    "SCHEMA": env("GRAPHENE_SCHEMA", default="config.schema.schema"),
    "MIDDLEWARE": [
        # Use GraphQL execution middleware (Graphene middleware class)
        "rail_django_graphql.middleware.performance_middleware.GraphQLExecutionMiddleware",
    ],
}

# Rail Django GraphQL Configuration (env-driven toggles)
RAIL_DJANGO_GRAPHQL = {
    "SCHEMAS": {
        "default": {
            "MODELS": [
                # 'apps.users.models.User',
                # 'apps.blog.models.Post',
                "apps.blog.models.Category",
                "apps.blog.models.Tag",
                "apps.blog.models.Comment",
            ],
            "SCHEMA_OVERRIDES": {
                "SCHEMA_SETTINGS": {
                    "excluded_models": [
                        "apps.users.models.User",
                    ]
                }
            },
            "ENABLE_MUTATIONS": True,
            "ENABLE_FILTERS": True,
            "ENABLE_PAGINATION": True,
            "ENABLE_SUBSCRIPTIONS": False,
            "MAX_PAGE_SIZE": 100,
            "DEFAULT_PAGE_SIZE": 20,
        }
    },
    "SECURITY": {
        "ENABLE_INTROSPECTION": env.bool("ENABLE_INTROSPECTION", default=True),
        "ENABLE_GRAPHIQL": env.bool("ENABLE_GRAPHIQL", default=True),
        "MAX_QUERY_DEPTH": env.int("GRAPHQL_MAX_QUERY_DEPTH", default=10),
        "MAX_QUERY_COMPLEXITY": env.int("GRAPHQL_MAX_QUERY_COMPLEXITY", default=1000),
    },
    "PERFORMANCE": {
        "ENABLE_CACHING": env.bool("GRAPHQL_ENABLE_CACHING", default=True),
        "CACHE_TIMEOUT": env.int("GRAPHQL_CACHE_TIMEOUT", default=300),
        "ENABLE_DATALOADER": env.bool("GRAPHQL_ENABLE_DATALOADER", default=True),
    },
    "SCHEMA_OVERRIDES": {
        "default": {
            "SCHEMA_SETTINGS": {
                "excluded_apps": [
                    "django.contrib.admin",  # exclude admin
                    # 'apps.blog',             # exclude entire blog app
                ],
                "excluded_models": [
                    # 'users.User',            # exclude via app_label.Model
                    "Tag",  # exclude by model class name
                    "apps.blog.models.Comment",  # fully-qualified model path also supported
                ],
                "enable_pagination": True,
                "auto_refresh_on_model_change": True,
                "enable_introspection": True,
                "auto_camelcase": False,
            },
            "TYPE_SETTINGS": {
                "EXCLUDE_FIELDS": {
                    "User": ["password", "last_login"],
                    "Post": ["secret_token"],
                },
                "ENABLE_AUTO_CAMEL_CASE": True,  # alias for auto_camelcase
                "GENERATE_FILTERS": True,
                "GENERATE_DESCRIPTIONS": True,
            },
            "QUERY_SETTINGS": {
                "ENABLE_PAGINATION": True,
                "DEFAULT_PAGE_SIZE": 50,
                "MAX_PAGE_SIZE": 200,
                "GENERATE_FILTERS": True,
                "GENERATE_ORDERING": True,
                "USE_RELAY": False,
                "ADDITIONAL_LOOKUP_FIELDS": {
                    "Post": ["slug"],
                    "User": ["uuid"],
                },
            },
            "MUTATION_SETTINGS": {
                "enable_nested_relations": True,
                "nested_relations_config": {
                    "Post": True,  # enable nested for Post relationships
                },
                "nested_field_config": {
                    "Post": {"tags": True},  # allow nested operations on Post.tags
                },
                "generate_bulk": True,
                "bulk_batch_size": 100,
                "enable_method_mutations": False,
                "required_update_fields": {
                    "User": ["email"],
                },
                "generate_create": True,
                "generate_update": True,
                "generate_delete": True,
                "enable_create": True,  # aliases kept for compatibility
                "enable_update": True,
                "enable_delete": True,
                "enable_bulk_operations": True,
            },
        }
    },
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
)

CORS_ALLOW_CREDENTIALS = env.bool("CORS_ALLOW_CREDENTIALS", default=True)

# Optional cache configuration via Redis
_redis_url = env("REDIS_URL", default=None)
if _redis_url:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": _redis_url,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "IGNORE_EXCEPTIONS": True,
            },
        }
    }

# Logging level
LOG_LEVEL = env("LOG_LEVEL", default="INFO")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
}

# Optional Email configuration
_email_url = env("EMAIL_URL", default=None)
if _email_url:
    EMAIL_CONFIG = env.email_url("EMAIL_URL")
    vars().update(EMAIL_CONFIG)
else:
    EMAIL_BACKEND = env(
        "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
    )
    EMAIL_HOST = env("EMAIL_HOST", default=None)
    EMAIL_PORT = env.int("EMAIL_PORT", default=587)
    EMAIL_HOST_USER = env("EMAIL_USER", default=None)
    EMAIL_HOST_PASSWORD = env("EMAIL_PASS", default=None)
    EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
