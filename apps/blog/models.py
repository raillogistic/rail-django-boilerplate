from math import perm

from django.conf import settings
from django.db import models
from datetime import date

# Import security features
from .security import BlogRoles, encrypt_sensitive_field, FieldAccessLevel, secure_model

# import mutation decorator
# from rail_django_graphql.core.decorators import mutation


@secure_model({
    'required_roles': [BlogRoles.EDITOR, BlogRoles.ADMIN],
    'audit_operations': ['create', 'update', 'delete'],
    'field_permissions': {
        'is_active': FieldAccessLevel.ADMIN_ONLY,
    }
})
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


@secure_model({
    'required_roles': [BlogRoles.EDITOR, BlogRoles.ADMIN],
    'audit_operations': ['create', 'update', 'delete'],
    'field_permissions': {
        'is_active': FieldAccessLevel.ADMIN_ONLY,
    }
})
class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    color = models.CharField(max_length=7, default='#000000')  # Hex color
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


@secure_model({
    'required_roles': [BlogRoles.AUTHOR, BlogRoles.EDITOR, BlogRoles.ADMIN],
    'audit_operations': ['create', 'update', 'delete'],
    'field_permissions': {
        'status': FieldAccessLevel.OWNER_OR_ADMIN,
        'is_featured': FieldAccessLevel.ADMIN_ONLY,
        'view_count': FieldAccessLevel.READ_ONLY,
    }
})
class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField(blank=True)
    excerpt = models.TextField(max_length=500, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="posts"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts")
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('published', 'Published'),
            ('archived', 'Archived'),
        ],
        default='draft'
    )
    featured_image = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def test_prop(self) -> date:
        return self.created_at

    # test_prop.fget.short_description = ""


@secure_model({
    'required_roles': [BlogRoles.READER, BlogRoles.AUTHOR, BlogRoles.EDITOR, BlogRoles.ADMIN],
    'audit_operations': ['create', 'update', 'delete'],
    'field_permissions': {
        'is_approved': FieldAccessLevel.ADMIN_ONLY,
        'is_flagged': FieldAccessLevel.ADMIN_ONLY,
    }
})
class Comment(models.Model):
    """Comments on blog posts with moderation."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField()
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    is_approved = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"


@secure_model({
    'sensitive_fields': ['email'],
    'required_roles': [BlogRoles.ADMIN, BlogRoles.EDITOR],
    'audit_operations': ['create', 'update', 'delete'],
    'field_permissions': {
        'email': FieldAccessLevel.ADMIN_ONLY,
        'preferences': FieldAccessLevel.OWNER_OR_ADMIN,
    }
})
class Subscriber(models.Model):
    """Newsletter subscribers with encrypted email."""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    preferences = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Subscriber: {self.email}"


@secure_model({
    'required_roles': [BlogRoles.ADMIN],
    'audit_operations': ['update'],
    'field_permissions': {
        'posts_per_page': FieldAccessLevel.ADMIN_ONLY,
        'moderate_comments': FieldAccessLevel.ADMIN_ONLY,
        'seo_settings': FieldAccessLevel.ADMIN_ONLY,
    }
})
class BlogSettings(models.Model):
    """Global blog settings."""
    site_title = models.CharField(max_length=200, default="My Blog")
    site_description = models.TextField(blank=True)
    posts_per_page = models.PositiveIntegerField(default=10)
    allow_comments = models.BooleanField(default=True)
    moderate_comments = models.BooleanField(default=True)
    enable_newsletter = models.BooleanField(default=True)
    social_links = models.JSONField(default=dict, blank=True)
    seo_settings = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Blog Settings"
        verbose_name_plural = "Blog Settings"

    def __str__(self):
        return f"Blog Settings: {self.site_title}"

    def save(self, *args, **kwargs):
        # Ensure only one settings instance exists
        if not self.pk and BlogSettings.objects.exists():
            raise ValueError("Only one BlogSettings instance is allowed")
        super().save(*args, **kwargs)
