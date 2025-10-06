# Security Setup Guide

This guide provides comprehensive instructions for setting up and configuring security features in the Django GraphQL boilerplate.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Configuration](#configuration)
4. [Security Features](#security-features)
5. [Verification](#verification)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

Before setting up security features, ensure you have:

- Python 3.8+
- Django 4.2+
- Required dependencies installed:
  ```bash
  pip install pyotp PyJWT
  ```

## Initial Setup

### 1. Run Security Setup Command

Execute the automated security setup command:

```bash
python manage.py setup_security
```

This command will:
- ✅ Verify prerequisites
- ✅ Create necessary directories (`logs/`, `security/`, `media/qr_codes/`)
- ✅ Configure security middlewares
- ✅ Set up audit logging
- ✅ Create log files

### 2. Create Database Tables

Run migrations to create security-related tables:

```bash
python manage.py migrate
```

Note: The `rail_django_graphql` package is now installed as an external dependency, so migrations are included with the package.

### 3. Create Cache Table

For database-backed caching (fallback when Redis is not available):

```bash
python manage.py createcachetable
```

## Configuration

### Base Settings

The security configuration is already integrated into `config/settings/base.py`:

```python
# Authentication & JWT Configuration
GRAPHQL_JWT = {
    'JWT_ALGORITHM': 'HS256',
    'JWT_EXPIRATION_DELTA': timedelta(hours=1),
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),
    'JWT_ALLOW_REFRESH': True,
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
}

# Cache Configuration (with Redis fallback to database)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    } if env('REDIS_URL', default=None) else {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}

# GraphQL Security Settings
GRAPHQL_SECURITY = {
    'AUTHENTICATION_REQUIRED': True,
    'RATE_LIMITING': {
        'ENABLED': True,
        'REQUESTS_PER_MINUTE': 60,
        'BURST_LIMIT': 10,
    },
    'SECURITY_HEADERS': {
        'ENABLE_CORS': True,
        'CORS_ALLOW_CREDENTIALS': True,
        'CORS_ALLOWED_ORIGINS': [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
    }
}

# Multi-Factor Authentication Configuration
MFA_CONFIG = {
    'ENABLED': False,  # Set to True to enable MFA
    'ISSUER_NAME': 'Django GraphQL Boilerplate',
    'QR_CODE_SIZE': 200,
    'BACKUP_CODES_COUNT': 10,
    'TRUSTED_DEVICE_EXPIRY_DAYS': 30,
}

# Audit Logging Configuration
AUDIT_CONFIG = {
    'ENABLED': True,
    'STORE_IN_DATABASE': True,
    'STORE_IN_FILE': True,
    'RETENTION_DAYS': 90,
    'ALERT_THRESHOLDS': {
        'failed_logins_per_ip': 10,
        'failed_logins_per_user': 5,
        'suspicious_activity_window': 300,
    }
}
```

### Environment Variables

Create a `.env` file with the following variables:

```env
# Security
SECRET_KEY=your-secret-key-here
DEBUG=False

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Cache (Optional - Redis)
REDIS_URL=redis://127.0.0.1:6379/1

# Email (Optional)
EMAIL_URL=smtp://user:password@localhost:587

# Production Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Security Features

### 1. Authentication Middleware

- **GraphQLAuthenticationMiddleware**: Handles JWT token validation
- **Location**: `rail_django_graphql.middleware.auth.GraphQLAuthenticationMiddleware`

### 2. Rate Limiting

- **GraphQLRateLimitMiddleware**: Prevents abuse with configurable limits
- **Location**: `rail_django_graphql.middleware.rate_limit.GraphQLRateLimitMiddleware`

### 3. Multi-Factor Authentication (MFA)

- **TOTP-based authentication** using `pyotp`
- **Backup codes** for account recovery
- **Trusted devices** to reduce MFA prompts
- **QR code generation** for authenticator apps

### 4. Audit Logging

- **Comprehensive event tracking**:
  - Login attempts (success/failure)
  - Account lockouts
  - Suspicious activities
  - Rate limiting events
  - MFA events

- **Storage options**:
  - Database storage (`AuditEventModel`)
  - File logging (`logs/audit.log`)
  - External webhook support

### 5. Security Headers

- **XSS Protection**: `SECURE_BROWSER_XSS_FILTER = True`
- **Content Type Sniffing**: `SECURE_CONTENT_TYPE_NOSNIFF = True`
- **Frame Options**: `X_FRAME_OPTIONS = 'DENY'`

## Verification

### Run Security Check

Verify your security configuration:

```bash
python manage.py security_check
```

This command checks:
- ✅ Middleware configuration
- ✅ Audit logging setup
- ✅ MFA configuration
- ✅ Rate limiting setup
- ✅ Django security settings
- ✅ Database tables
- ✅ Cache configuration

### Expected Output

```
=== VÉRIFICATION DE SÉCURITÉ GRAPHQL ===

✅ Configuration des Middlewares
✅ Configuration d'Audit
✅ Configuration MFA
✅ Limitation de Débit
✅ Paramètres de Sécurité Django
✅ Configuration Base de Données
✅ Configuration Cache

=== RECOMMANDATIONS ===
💡 Considérer l'activation de l'authentification multi-facteurs (MFA)

✅ Configuration de sécurité validée avec succès!
```

## Production Deployment

### 1. Environment Configuration

For production, update your environment variables:

```env
DEBUG=False
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

### 2. Enable MFA

Update `MFA_CONFIG` in settings:

```python
MFA_CONFIG = {
    'ENABLED': True,  # Enable MFA for production
    'ISSUER_NAME': 'Your Production App Name',
    'QR_CODE_SIZE': 200,
    'BACKUP_CODES_COUNT': 10,
    'TRUSTED_DEVICE_EXPIRY_DAYS': 30,
}
```

### 3. Configure Redis

For production, use Redis for caching:

```env
REDIS_URL=redis://your-redis-server:6379/1
```

### 4. Set up Log Rotation

Configure log rotation for audit logs:

```bash
# Add to /etc/logrotate.d/django-graphql
/path/to/your/app/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
```

## Troubleshooting

### Common Issues

#### 1. AppRegistryNotReady Error

**Problem**: Django apps not loaded during migrations.

**Solution**: Ensure schema registration is not in `config/__init__.py`. Move to app's `ready()` method.

#### 2. SQLite JSON_VALID Error

**Problem**: SQLite doesn't support JSONField validation.

**Solution**: Already fixed - using TextField with JSON serialization.

#### 3. Cache Table Missing

**Problem**: Database cache backend table doesn't exist.

**Solution**:
```bash
python manage.py createcachetable
```

#### 4. Missing Dependencies

**Problem**: `pyotp` or `PyJWT` not installed.

**Solution**:
```bash
pip install pyotp PyJWT
```

### Debug Mode

For debugging security issues, temporarily enable debug logging:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'rail_django_graphql': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Security Checklist

Before going to production:

- [ ] Run `python manage.py security_check`
- [ ] Verify all migrations applied
- [ ] Test authentication flow
- [ ] Test rate limiting
- [ ] Configure proper SECRET_KEY
- [ ] Enable HTTPS
- [ ] Set up monitoring for audit logs
- [ ] Configure backup strategy
- [ ] Test MFA functionality (if enabled)
- [ ] Verify CORS settings

## Support

For additional support:

1. Check the [main documentation](./README.md)
2. Review [middleware documentation](./middleware/README.md)
3. Check [extensions documentation](./extensions/README.md)
4. Review security logs in `logs/security.log`

## Security Best Practices

1. **Regular Updates**: Keep dependencies updated
2. **Log Monitoring**: Monitor audit logs for suspicious activity
3. **Access Control**: Implement proper permission checks
4. **Rate Limiting**: Adjust limits based on usage patterns
5. **MFA**: Enable for all admin accounts
6. **Backup**: Regular backups of audit logs and user data
7. **Testing**: Regular security testing and penetration testing