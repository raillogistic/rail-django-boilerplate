"""Security features for Django GraphQL blog application.
Provides decorators and utilities for securing GraphQL operations."""
import logging
import hashlib
import json
from functools import wraps
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser


# Configure logging
logger = logging.getLogger(__name__)


class FieldAccessLevel(Enum):
    """Field access levels for GraphQL security."""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    OWNER_OR_ADMIN = "owner_or_admin"
    ADMIN_ONLY = "admin_only"
    READ_ONLY = "read_only"


class BlogRoles(Enum):
    """Blog-specific roles for RBAC."""
    ADMIN = "ADMIN"
    EDITOR = "EDITOR"
    AUTHOR = "AUTHOR"
    READER = "READER"
    MODERATOR = "MODERATOR"


# Security decorator for models
def secure_model(security_config: Dict[str, Any]):
    """
    Decorator to apply security configuration to Django models.
    
    Args:
        security_config: Dictionary containing security settings
            - required_roles: List of roles required to access the model
            - audit_operations: List of operations to audit
            - field_permissions: Dict mapping field names to access levels
            - sensitive_fields: List of fields containing sensitive data
    
    Returns:
        Decorated model class with security metadata
    """
    def decorator(model_class):
        # Store security configuration on the model
        model_class._graphql_security = security_config
        
        # Add security validation methods
        def check_field_access(self, field_name: str, user, operation: str = 'read') -> bool:
            """Check if user has access to a specific field."""
            if not hasattr(self.__class__, '_graphql_security'):
                return True
                
            field_permissions = self.__class__._graphql_security.get('field_permissions', {})
            access_level = field_permissions.get(field_name, FieldAccessLevel.PUBLIC)
            
            if access_level == FieldAccessLevel.PUBLIC:
                return True
            elif access_level == FieldAccessLevel.AUTHENTICATED:
                return not isinstance(user, AnonymousUser)
            elif access_level == FieldAccessLevel.OWNER_OR_ADMIN:
                return (hasattr(self, 'author') and self.author == user) or user.is_staff
            elif access_level == FieldAccessLevel.ADMIN_ONLY:
                return user.is_staff or user.is_superuser
            elif access_level == FieldAccessLevel.READ_ONLY:
                return operation == 'read'
            
            return False
        
        def check_role_access(self, user, required_roles: List[str]) -> bool:
            """Check if user has required roles."""
            if not required_roles:
                return True
                
            if isinstance(user, AnonymousUser):
                return False
                
            # Check if user is admin (always has access)
            if user.is_staff or user.is_superuser:
                return True
                
            # Check user roles (simplified - in real app, use proper RBAC)
            user_roles = getattr(user, 'roles', [])
            return any(role in required_roles for role in user_roles)
        
        # Add methods to model class
        model_class.check_field_access = check_field_access
        model_class.check_role_access = check_role_access
        
        return model_class
    
    return decorator


def secure_resolver(required_roles: Optional[List[str]] = None, 
                   audit: bool = False,
                   validate_input: bool = True):
    """
    Decorator for securing GraphQL resolvers.
    
    Args:
        required_roles: List of roles required to access the resolver
        audit: Whether to audit this operation
        validate_input: Whether to validate input data
    
    Returns:
        Decorated resolver function
    """
    def decorator(resolver_func: Callable) -> Callable:
        @wraps(resolver_func)
        def wrapper(self, info, **kwargs):
            user = info.context.user
            
            # Check authentication
            if required_roles and isinstance(user, AnonymousUser):
                raise PermissionDenied("Authentication required")
            
            # Check roles
            if required_roles:
                user_roles = getattr(user, 'roles', [])
                if not any(role in required_roles for role in user_roles) and not user.is_staff:
                    raise PermissionDenied("Insufficient permissions")
            
            # Audit logging
            if audit:
                logger.info(f"GraphQL operation: {resolver_func.__name__} by user: {user.username if hasattr(user, 'username') else 'anonymous'}")
            
            # Input validation
            if validate_input and kwargs:
                _validate_input_data(kwargs)
            
            return resolver_func(self, info, **kwargs)
        
        return wrapper
    return decorator


def encrypt_sensitive_field(field_name: str):
    """
    Decorator to encrypt sensitive fields.
    
    Args:
        field_name: Name of the field to encrypt
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, info, *args, **kwargs):
            result = func(self, info, *args, **kwargs)
            
            # In a real implementation, you would encrypt the specified field
            # For now, we just log that encryption would occur
            logger.info(f"ENCRYPTION: Field '{field_name}' would be encrypted")
            
            return result
        
        return wrapper
    return decorator


def require_authentication(resolver_func: Callable) -> Callable:
    """Decorator to require authentication for a resolver."""
    @wraps(resolver_func)
    def wrapper(self, info, *args, **kwargs):
        if isinstance(info.context.user, AnonymousUser):
            raise PermissionDenied("Authentication required")
        return resolver_func(self, info, *args, **kwargs)
    return wrapper


def require_role(role: str):
    """Decorator to require a specific role for a resolver."""
    def decorator(resolver_func: Callable) -> Callable:
        @wraps(resolver_func)
        def wrapper(self, info, *args, **kwargs):
            user = info.context.user
            if isinstance(user, AnonymousUser):
                raise PermissionDenied("Authentication required")
            
            user_roles = getattr(user, 'roles', [])
            if role not in user_roles and not user.is_staff:
                raise PermissionDenied(f"Role '{role}' required")
            
            return resolver_func(self, info, *args, **kwargs)
        return wrapper
    return decorator


def validate_input(required_fields: List[str]):
    """
    Decorator to validate input fields for GraphQL operations.
    
    Args:
        required_fields: List of field names that are required
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, info, *args, **kwargs):
            # For mutations, input is typically in kwargs or args
            input_data = kwargs.get('input', {}) if kwargs else {}
            
            # Validate required fields
            missing_fields = []
            for field in required_fields:
                if field not in input_data or not input_data[field]:
                    missing_fields.append(field)
            
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")
            
            # Basic sanitization
            for field, value in input_data.items():
                if isinstance(value, str):
                    # Remove potentially dangerous HTML/script tags
                    input_data[field] = value.replace('<script>', '').replace('</script>', '')
            
            return func(self, info, *args, **kwargs)
        
        return wrapper
    return decorator


def audit_operation(operation_name: str):
    """
    Decorator to audit GraphQL operations.
    
    Args:
        operation_name: Name of the operation being audited
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Handle both method calls (with self, info) and function calls
            if len(args) >= 2 and hasattr(args[1], 'context'):
                # GraphQL resolver method call
                info = args[1]
                user = getattr(info.context, 'user', 'Anonymous')
            else:
                # Regular function call
                user = 'Test'
            
            logger.info(f"AUDIT: {operation_name} performed by {user}")
            
            try:
                result = func(*args, **kwargs)
                logger.info(f"AUDIT: {operation_name} completed successfully")
                return result
            except Exception as e:
                logger.error(f"AUDIT: {operation_name} failed: {str(e)}")
                raise
        
        return wrapper
    return decorator


def _validate_input_data(data: Dict[str, Any]) -> None:
    """
    Validate input data for security issues.
    
    Args:
        data: Input data to validate
    
    Raises:
        ValueError: If validation fails
    """
    # Check for common injection patterns
    dangerous_patterns = ['<script', 'javascript:', 'onload=', 'onerror=', 'DROP TABLE', 'DELETE FROM']
    
    def check_value(value):
        if isinstance(value, str):
            value_lower = value.lower()
            for pattern in dangerous_patterns:
                if pattern.lower() in value_lower:
                    raise ValueError(f"Potentially dangerous input detected: {pattern}")
        elif isinstance(value, dict):
            for v in value.values():
                check_value(v)
        elif isinstance(value, list):
            for item in value:
                check_value(item)
    
    for value in data.values():
        check_value(value)


# Security configuration registry
SECURITY_REGISTRY = {
    'blog_roles': {
        BlogRoles.ADMIN.value: {
            'permissions': ['create', 'read', 'update', 'delete', 'publish', 'moderate'],
            'description': 'Full access to all blog operations'
        },
        BlogRoles.EDITOR.value: {
            'permissions': ['create', 'read', 'update', 'delete', 'publish'],
            'description': 'Can manage content but not system settings'
        },
        BlogRoles.AUTHOR.value: {
            'permissions': ['create', 'read', 'update'],
            'description': 'Can create and edit own content'
        },
        BlogRoles.READER.value: {
            'permissions': ['read'],
            'description': 'Can read published content'
        },
        BlogRoles.MODERATOR.value: {
            'permissions': ['read', 'moderate'],
            'description': 'Can moderate comments and content'
        }
    }
}