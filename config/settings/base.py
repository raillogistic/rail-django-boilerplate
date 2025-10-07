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

disable_security_mutations = False

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
    # Middlewares de sécurité GraphQL
    "rail_django_graphql.middleware.GraphQLAuthenticationMiddleware",
    "rail_django_graphql.middleware.GraphQLRateLimitMiddleware",
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

# Rail Django GraphQL Configuration (aligned with dataclass-based settings)

RAIL_DJANGO_GRAPHQL = {
    # Core schema configuration
    "DEFAULT_SCHEMA": "default",
    "ENABLE_GRAPHIQL": env.bool("ENABLE_GRAPHIQL", default=True),
    "ENABLE_INTROSPECTION": env.bool("ENABLE_INTROSPECTION", default=True),
    "AUTHENTICATION_REQUIRED": False,
    "PERMISSION_CLASSES": [],
    # Schema-specific configurations
    "SCHEMAS": {
        "default": {
            "MODELS": [
                # 'apps.users.models.User',
                # 'apps.blog.models.Post',
                "apps.blog.models.Category",
                "apps.blog.models.Tag",
                "apps.blog.models.Comment",
            ],
            # Schema settings (aligned with SchemaSettings dataclass)
            "SCHEMA_SETTINGS": {
                "excluded_apps": ["blog"],
                "excluded_models": [
                    "Post",
                    "apps.users.models.User",
                ],
                "enable_introspection": env.bool("ENABLE_INTROSPECTION", default=True),
                "enable_graphiql": env.bool("ENABLE_GRAPHIQL", default=True),
                "auto_refresh_on_model_change": True,
                "enable_pagination": True,
                "auto_camelcase": False,
            },
            # Query settings (aligned with QueryGeneratorSettings dataclass)
            "QUERY_SETTINGS": {
                "generate_filters": False,  # Explicitly disabled
                "generate_ordering": True,
                "generate_pagination": True,
                "enable_pagination": True,
                "enable_ordering": True,
                "use_relay": False,
                "default_page_size": 20,
                "max_page_size": 100,
                "additional_lookup_fields": {},
            },
            # Mutation settings (aligned with MutationGeneratorSettings dataclass)
            "MUTATION_SETTINGS": {
                "generate_create": True,
                "generate_update": True,
                "generate_delete": True,
                "generate_bulk": False,
                "enable_create": True,
                "enable_update": True,
                "enable_delete": True,
                "enable_bulk_operations": False,
                "enable_method_mutations": False,
                "bulk_batch_size": 100,
                "required_update_fields": {},
                "enable_nested_relations": True,
                "nested_relations_config": {},
                "nested_field_config": {},
            },
            # Type generation settings (aligned with TypeGeneratorSettings dataclass)
            "TYPE_GENERATION_SETTINGS": {
                "exclude_fields": {},
                "excluded_fields": {},
                "include_fields": None,
                "custom_field_mappings": {},
                "generate_filters": False,  # Explicitly disabled
                "enable_filtering": False,  # Explicitly disabled
                "auto_camelcase": False,
                "generate_descriptions": True,
            },
        }
    },
    # Legacy compatibility settings (deprecated but maintained for backward compatibility)
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

# Cache configuration (required for security features)
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
else:
    # Fallback to database cache for development
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "cache_table",
        }
    }

# JWT Authentication Configuration
JWT_SECRET_KEY = env("JWT_SECRET_KEY", default=SECRET_KEY)
JWT_ALGORITHM = env("JWT_ALGORITHM", default="HS256")
JWT_ACCESS_TOKEN_LIFETIME = env.int("JWT_ACCESS_TOKEN_LIFETIME", default=3600)  # 1 hour
JWT_REFRESH_TOKEN_LIFETIME = env.int(
    "JWT_REFRESH_TOKEN_LIFETIME", default=86400
)  # 24 hours
JWT_ISSUER = env("JWT_ISSUER", default="django-graphql-boilerplate")
JWT_AUDIENCE = env("JWT_AUDIENCE", default="django-graphql-api")

# Security Middleware Configuration
GRAPHQL_SECURITY = {
    # Authentication settings
    "AUTHENTICATION": {
        "ENABLED": env.bool("GRAPHQL_AUTH_ENABLED", default=True),
        "JWT_SECRET_KEY": JWT_SECRET_KEY,
        "JWT_ALGORITHM": JWT_ALGORITHM,
        "JWT_ACCESS_TOKEN_LIFETIME": JWT_ACCESS_TOKEN_LIFETIME,
        "JWT_REFRESH_TOKEN_LIFETIME": JWT_REFRESH_TOKEN_LIFETIME,
        "JWT_ISSUER": JWT_ISSUER,
        "JWT_AUDIENCE": JWT_AUDIENCE,
        "REQUIRE_AUTHENTICATION": env.bool("GRAPHQL_REQUIRE_AUTH", default=False),
        "ANONYMOUS_QUERIES_ALLOWED": env.bool("GRAPHQL_ALLOW_ANONYMOUS", default=True),
        "USER_CACHE_TIMEOUT": env.int(
            "GRAPHQL_USER_CACHE_TIMEOUT", default=300
        ),  # 5 minutes
    },
    # Rate limiting settings
    "RATE_LIMITING": {
        "ENABLED": env.bool("GRAPHQL_RATE_LIMIT_ENABLED", default=True),
        "ANONYMOUS_LIMIT": env.int(
            "GRAPHQL_ANONYMOUS_RATE_LIMIT", default=100
        ),  # per hour
        "AUTHENTICATED_LIMIT": env.int(
            "GRAPHQL_AUTH_RATE_LIMIT", default=1000
        ),  # per hour
        "LOGIN_LIMIT": env.int("GRAPHQL_LOGIN_RATE_LIMIT", default=10),  # per hour
        "CACHE_KEY_PREFIX": env(
            "GRAPHQL_RATE_LIMIT_PREFIX", default="graphql_rate_limit"
        ),
        "WINDOW_SIZE": env.int("GRAPHQL_RATE_LIMIT_WINDOW", default=3600),  # 1 hour
    },
    # Security headers
    "SECURITY_HEADERS": {
        "ENABLE_CORS_HEADERS": env.bool("GRAPHQL_ENABLE_CORS", default=True),
        "ENABLE_CSP_HEADERS": env.bool("GRAPHQL_ENABLE_CSP", default=True),
        "ENABLE_SECURITY_HEADERS": env.bool(
            "GRAPHQL_ENABLE_SECURITY_HEADERS", default=True
        ),
    },
}

# Multi-Factor Authentication (MFA) Configuration
MFA_CONFIG = {
    "ENABLED": env.bool("MFA_ENABLED", default=False),
    "TOTP_ISSUER": env("MFA_TOTP_ISSUER", default="Django GraphQL Boilerplate"),
    "BACKUP_CODES_COUNT": env.int("MFA_BACKUP_CODES_COUNT", default=10),
    "TRUSTED_DEVICE_LIFETIME": env.int(
        "MFA_TRUSTED_DEVICE_LIFETIME", default=2592000
    ),  # 30 days
    "SMS_PROVIDER": env("MFA_SMS_PROVIDER", default=None),  # Optional SMS provider
    "SMS_CONFIG": {
        "API_KEY": env("MFA_SMS_API_KEY", default=None),
        "FROM_NUMBER": env("MFA_SMS_FROM_NUMBER", default=None),
    },
}

# Audit Logging Configuration
AUDIT_CONFIG = {
    "ENABLED": env.bool("AUDIT_ENABLED", default=True),
    "LOG_LEVEL": env("AUDIT_LOG_LEVEL", default="INFO"),
    "LOG_FILE": env("AUDIT_LOG_FILE", default=str(BASE_DIR / "logs" / "audit.log")),
    "MAX_LOG_SIZE": env.int("AUDIT_MAX_LOG_SIZE", default=10485760),  # 10MB
    "BACKUP_COUNT": env.int("AUDIT_BACKUP_COUNT", default=5),
    "DATABASE_LOGGING": env.bool("AUDIT_DATABASE_LOGGING", default=True),
    "WEBHOOK_URL": env("AUDIT_WEBHOOK_URL", default=None),
    "WEBHOOK_SECRET": env("AUDIT_WEBHOOK_SECRET", default=None),
    "ALERT_THRESHOLDS": {
        "FAILED_LOGINS": env.int("AUDIT_FAILED_LOGIN_THRESHOLD", default=5),
        "SUSPICIOUS_ACTIVITY": env.int("AUDIT_SUSPICIOUS_THRESHOLD", default=10),
        "RATE_LIMIT_EXCEEDED": env.int("AUDIT_RATE_LIMIT_THRESHOLD", default=20),
    },
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

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

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
