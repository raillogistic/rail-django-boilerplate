# GraphQL Security Documentation

## Overview

This documentation covers the comprehensive security features available in the `rail-django-graphql` package, including the `GraphqlMeta` metaclass for Django models and integrated security measures.

## Table of Contents

1. [GraphqlMeta Metaclass](#graphqlmeta-metaclass)
2. [Security Features](#security-features)
3. [Configuration](#configuration)
4. [Usage Examples](#usage-examples)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## GraphqlMeta Metaclass

The `GraphqlMeta` metaclass automatically applies security features to Django models when used in GraphQL schemas.

### Basic Usage

```python
from django.db import models
from rail_django_graphql.security import GraphqlMeta, FieldAccessLevel

class MyModel(models.Model, metaclass=GraphqlMeta):
    name = models.CharField(max_length=100)
    sensitive_data = models.TextField()
    
    class Meta:
        graphql_security = {
            'required_roles': ['ADMIN', 'EDITOR'],
            'audit_operations': ['create', 'update', 'delete'],
            'sensitive_fields': ['sensitive_data'],
            'field_permissions': {
                'sensitive_data': FieldAccessLevel.ADMIN_ONLY,
            }
        }
```

### Security Configuration Options

#### Required Roles
Define which roles can access the model:

```python
class Meta:
    graphql_security = {
        'required_roles': ['ADMIN', 'EDITOR', 'AUTHOR'],
    }
```

#### Audit Operations
Specify which operations should be audited:

```python
class Meta:
    graphql_security = {
        'audit_operations': ['create', 'update', 'delete', 'read'],
    }
```

#### Sensitive Fields
Mark fields as sensitive for encryption and access control:

```python
class Meta:
    graphql_security = {
        'sensitive_fields': ['email', 'phone', 'ssn'],
    }
```

#### Field-Level Permissions
Control access to specific fields:

```python
from rail_django_graphql.security import FieldAccessLevel

class Meta:
    graphql_security = {
        'field_permissions': {
            'is_active': FieldAccessLevel.ADMIN_ONLY,
            'status': FieldAccessLevel.OWNER_OR_ADMIN,
            'view_count': FieldAccessLevel.READ_ONLY,
            'email': FieldAccessLevel.ADMIN_ONLY,
        }
    }
```

## Security Features

### 1. Authentication & Authorization

#### Role-Based Access Control (RBAC)

```python
from rail_django_graphql.security import require_role, BlogRoles

@require_role([BlogRoles.ADMIN, BlogRoles.EDITOR])
def resolve_sensitive_data(self, info):
    return SensitiveModel.objects.all()
```

#### Authentication Decorators

```python
from rail_django_graphql.security import require_authentication

@require_authentication
def resolve_user_data(self, info):
    return info.context.user.profile
```

### 2. Input Validation

```python
from rail_django_graphql.security import validate_input

@validate_input(['email', 'name', 'content'])
def mutate(root, info, **kwargs):
    # Input is automatically validated and sanitized
    return create_object(**kwargs)
```

### 3. Field Encryption

```python
from rail_django_graphql.security import encrypt_sensitive_field

@encrypt_sensitive_field('email')
class User(models.Model, metaclass=GraphqlMeta):
    email = models.EmailField()
    name = models.CharField(max_length=100)
```

### 4. Audit Logging

```python
from rail_django_graphql.security import audit_operation

@audit_operation('create_post')
def create_post(root, info, **kwargs):
    # Operation is automatically logged
    return Post.objects.create(**kwargs)
```

### 5. Query Security

#### Depth Limiting
```python
GRAPHQL_SECURITY = {
    'MAX_QUERY_DEPTH': 7,
}
```

#### Complexity Analysis
```python
GRAPHQL_SECURITY = {
    'MAX_QUERY_COMPLEXITY': 100,
}
```

#### Introspection Control
```python
GRAPHQL_SECURITY = {
    'ENABLE_INTROSPECTION': False,  # Disable in production
}
```

## Configuration

### Django Settings

```python
# settings.py

INSTALLED_APPS = [
    # ... other apps
    'rail_django_graphql.security',
]

MIDDLEWARE = [
    # ... other middleware
    'rail_django_graphql.middleware.GraphQLAuthenticationMiddleware',
    'rail_django_graphql.middleware.GraphQLRateLimitMiddleware',
    'rail_django_graphql.security.create_security_middleware',
]

GRAPHQL_SECURITY = {
    # Query Security
    'MAX_QUERY_DEPTH': 7,
    'MAX_QUERY_COMPLEXITY': 100,
    'ENABLE_INTROSPECTION': False,
    'QUERY_TIMEOUT': 10,
    
    # Rate Limiting
    'RATE_LIMIT_PER_MINUTE': 60,
    'RATE_LIMIT_BURST': 10,
    
    # Input Validation
    'ENABLE_INPUT_VALIDATION': True,
    'SANITIZE_HTML': True,
    'MAX_STRING_LENGTH': 10000,
    'ALLOWED_FILE_TYPES': ['.jpg', '.png', '.pdf'],
    
    # Field Encryption
    'ENCRYPTION_KEY': 'your-encryption-key-here',
    'ENCRYPT_SENSITIVE_FIELDS': True,
    
    # Audit Logging
    'ENABLE_AUDIT_LOGGING': True,
    'AUDIT_LOG_LEVEL': 'INFO',
    'AUDIT_SENSITIVE_OPERATIONS': True,
    
    # RBAC Configuration
    'DEFAULT_ROLES': ['USER', 'ADMIN'],
    'ROLE_HIERARCHY': {
        'ADMIN': ['EDITOR', 'AUTHOR', 'READER'],
        'EDITOR': ['AUTHOR', 'READER'],
        'AUTHOR': ['READER'],
    },
    
    # Sensitive Fields
    'SENSITIVE_FIELD_PATTERNS': [
        r'.*password.*',
        r'.*email.*',
        r'.*phone.*',
        r'.*ssn.*',
        r'.*credit_card.*',
    ],
    
    # Security Monitoring
    'ENABLE_SECURITY_MONITORING': True,
    'ALERT_ON_SUSPICIOUS_ACTIVITY': True,
    'MAX_FAILED_ATTEMPTS': 5,
    'LOCKOUT_DURATION': 300,  # 5 minutes
}
```

## Usage Examples

### Complete Model Example

```python
from django.db import models
from django.contrib.auth import get_user_model
from rail_django_graphql.security import (
    GraphqlMeta, 
    FieldAccessLevel, 
    encrypt_sensitive_field,
    BlogRoles
)

User = get_user_model()

@encrypt_sensitive_field('email')
class BlogPost(models.Model, metaclass=GraphqlMeta):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()  # Will be encrypted
    is_published = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        graphql_security = {
            'required_roles': [BlogRoles.AUTHOR, BlogRoles.EDITOR, BlogRoles.ADMIN],
            'audit_operations': ['create', 'update', 'delete'],
            'sensitive_fields': ['email'],
            'field_permissions': {
                'is_published': FieldAccessLevel.OWNER_OR_ADMIN,
                'view_count': FieldAccessLevel.READ_ONLY,
                'email': FieldAccessLevel.ADMIN_ONLY,
            }
        }
```

### GraphQL Schema with Security

```python
import graphene
from graphene_django import DjangoObjectType
from rail_django_graphql.security import (
    require_authentication,
    require_role,
    validate_input,
    audit_operation,
    secure_resolver
)

class BlogPostType(DjangoObjectType):
    class Meta:
        model = BlogPost
        fields = "__all__"

class Query(graphene.ObjectType):
    blog_posts = graphene.List(BlogPostType)
    
    @secure_resolver
    @require_authentication
    def resolve_blog_posts(self, info):
        return BlogPost.objects.filter(is_published=True)

class CreateBlogPost(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=True)
    
    blog_post = graphene.Field(BlogPostType)
    success = graphene.Boolean()
    
    @staticmethod
    @require_authentication
    @require_role([BlogRoles.AUTHOR, BlogRoles.EDITOR, BlogRoles.ADMIN])
    @validate_input(['title', 'content'])
    @audit_operation('create_blog_post')
    def mutate(root, info, **kwargs):
        blog_post = BlogPost.objects.create(
            author=info.context.user,
            **kwargs
        )
        return CreateBlogPost(blog_post=blog_post, success=True)
```

## Best Practices

### 1. Security Configuration

- Always disable introspection in production
- Set appropriate query depth and complexity limits
- Use strong encryption keys for sensitive fields
- Enable comprehensive audit logging

### 2. Role-Based Access Control

- Define clear role hierarchies
- Use principle of least privilege
- Regularly review and update role permissions
- Implement role inheritance properly

### 3. Input Validation

- Validate all user inputs
- Sanitize HTML content
- Set reasonable length limits
- Use whitelist approach for file uploads

### 4. Field-Level Security

- Mark sensitive fields appropriately
- Use field-level permissions granularly
- Encrypt PII and sensitive data
- Implement proper access controls

### 5. Monitoring and Auditing

- Enable comprehensive audit logging
- Monitor for suspicious activities
- Set up alerts for security events
- Regularly review audit logs

## Field Access Levels

```python
class FieldAccessLevel:
    PUBLIC = "public"              # Anyone can access
    AUTHENTICATED = "authenticated" # Authenticated users only
    OWNER_ONLY = "owner_only"      # Only the owner can access
    OWNER_OR_ADMIN = "owner_or_admin"  # Owner or admin can access
    ADMIN_ONLY = "admin_only"      # Only admins can access
    READ_ONLY = "read_only"        # Read-only access
    WRITE_ONLY = "write_only"      # Write-only access
```

## Security Decorators

### @secure_resolver
Applies comprehensive security checks to GraphQL resolvers:

```python
@secure_resolver
def resolve_sensitive_data(self, info):
    # Automatic security checks applied
    return get_sensitive_data()
```

### @require_authentication
Ensures user is authenticated:

```python
@require_authentication
def resolve_user_profile(self, info):
    return info.context.user.profile
```

### @require_role
Checks user roles:

```python
@require_role([BlogRoles.ADMIN, BlogRoles.EDITOR])
def resolve_admin_data(self, info):
    return get_admin_data()
```

### @validate_input
Validates and sanitizes input:

```python
@validate_input(['email', 'name'])
def create_user(root, info, **kwargs):
    return User.objects.create(**kwargs)
```

### @audit_operation
Logs operations for audit trail:

```python
@audit_operation('delete_user')
def delete_user(root, info, user_id):
    User.objects.get(id=user_id).delete()
```

## Troubleshooting

### Common Issues

1. **Permission Denied Errors**
   - Check user roles and permissions
   - Verify field access levels
   - Ensure proper authentication

2. **Validation Errors**
   - Review input validation rules
   - Check field length limits
   - Verify data types

3. **Encryption Issues**
   - Ensure encryption key is set
   - Check field encryption configuration
   - Verify database field types

4. **Performance Issues**
   - Review query complexity limits
   - Check depth limiting configuration
   - Monitor audit logging overhead

### Debug Mode

Enable debug mode for detailed security information:

```python
GRAPHQL_SECURITY = {
    'DEBUG_SECURITY': True,  # Only in development
    'LOG_SECURITY_EVENTS': True,
}
```

## Security Compliance

This implementation helps achieve compliance with:

- **GDPR**: Data encryption, access controls, audit trails
- **SOX**: Complete audit logging, data integrity
- **ISO 27001**: Documented security controls, monitoring
- **HIPAA**: Data encryption, access controls (when applicable)

## Support and Updates

For the latest security updates and best practices, refer to the official documentation and security advisories.