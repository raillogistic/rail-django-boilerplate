from math import perm

from django.conf import settings
from django.db import models
from datetime import date, datetime, timedelta
from django.db.models import Q, Count
from django.utils import timezone

# Import security features
from .security import BlogRoles, encrypt_sensitive_field, FieldAccessLevel, secure_model

# Import GraphQLMeta for testing
from rail_django_graphql.core.meta import GraphQLMeta

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

    class GraphQLMeta(GraphQLMeta):
        """GraphQL configuration for Category model."""
        
        # Quick filter configuration - search across category fields
        quick_filter_fields = [
            'name',
            'description',
            'slug',
        ]
        
        # Custom resolvers for specialized queries
        custom_resolvers = {
            'active_categories': 'get_active_categories',
            'popular_categories': 'get_popular_categories',
        }
        
        # Custom filters for advanced filtering
        custom_filters = {
            'has_posts': 'filter_has_posts',
            'post_count': 'filter_by_post_count',
        }
        
        # Standard filter fields
        filter_fields = {
            'name': ['exact', 'icontains', 'startswith'],
            'slug': ['exact', 'icontains'],
            'is_active': ['exact'],
            'created_at': ['exact', 'gt', 'gte', 'lt', 'lte', 'range'],
            'updated_at': ['exact', 'gt', 'gte', 'lt', 'lte', 'range'],
            'quick': ['icontains'],  # Enable quick filter
        }
        
        # Ordering fields
        ordering_fields = ['name', 'created_at', 'updated_at']

    def __str__(self):
        return self.name

    # Custom resolver methods for GraphQLMeta
    @classmethod
    def get_active_categories(cls, queryset, info, **kwargs):
        """Get only active categories."""
        return queryset.filter(is_active=True)

    @classmethod
    def get_popular_categories(cls, queryset, info, **kwargs):
        """Get categories with most posts."""
        return queryset.annotate(
            post_count=Count('posts')
        ).filter(
            is_active=True,
            post_count__gt=0
        ).order_by('-post_count')

    # Custom filter methods for GraphQLMeta
    @classmethod
    def filter_has_posts(cls, queryset, name, value):
        """Filter categories that have or don't have posts."""
        if value:
            return queryset.filter(posts__isnull=False).distinct()
        return queryset.filter(posts__isnull=True)

    @classmethod
    def filter_by_post_count(cls, queryset, name, value):
        """Filter by number of posts in category."""
        return queryset.annotate(
            post_count=Count('posts')
        ).filter(post_count=value)


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

    class GraphQLMeta(GraphQLMeta):
        """GraphQL configuration for Tag model."""
        
        # Quick filter configuration - search across tag fields
        quick_filter_fields = [
            'name',
            'slug',
        ]
        
        # Custom resolvers for specialized queries
        custom_resolvers = {
            'active_tags': 'get_active_tags',
            'popular_tags': 'get_popular_tags',
            'trending_tags': 'get_trending_tags',
        }
        
        # Custom filters for advanced filtering
        custom_filters = {
            'has_posts': 'filter_has_posts',
            'post_count': 'filter_by_post_count',
            'color_category': 'filter_by_color_category',
        }
        
        # Standard filter fields
        filter_fields = {
            'name': ['exact', 'icontains', 'startswith'],
            'slug': ['exact', 'icontains'],
            'color': ['exact'],
            'is_active': ['exact'],
            'created_at': ['exact', 'gt', 'gte', 'lt', 'lte', 'range'],
            'quick': ['icontains'],  # Enable quick filter
        }
        
        # Ordering fields
        ordering_fields = ['name', 'created_at']

    def __str__(self):
        return self.name

    # Custom resolver methods for GraphQLMeta
    @classmethod
    def get_active_tags(cls, queryset, info, **kwargs):
        """Get only active tags."""
        return queryset.filter(is_active=True)

    @classmethod
    def get_popular_tags(cls, queryset, info, **kwargs):
        """Get tags with most posts."""
        return queryset.annotate(
            post_count=Count('posts')
        ).filter(
            is_active=True,
            post_count__gt=0
        ).order_by('-post_count')

    @classmethod
    def get_trending_tags(cls, queryset, info, **kwargs):
        """Get tags used in recent posts."""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        return queryset.filter(
            posts__published_at__gte=thirty_days_ago,
            posts__status='published',
            is_active=True
        ).annotate(
            recent_post_count=Count('posts')
        ).order_by('-recent_post_count').distinct()

    # Custom filter methods for GraphQLMeta
    @classmethod
    def filter_has_posts(cls, queryset, name, value):
        """Filter tags that have or don't have posts."""
        if value:
            return queryset.filter(posts__isnull=False).distinct()
        return queryset.filter(posts__isnull=True)

    @classmethod
    def filter_by_post_count(cls, queryset, name, value):
        """Filter by number of posts with this tag."""
        return queryset.annotate(
            post_count=Count('posts')
        ).filter(post_count=value)

    @classmethod
    def filter_by_color_category(cls, queryset, name, value):
        """Filter by color category (light, dark, bright)."""
        if value == 'light':
            # Light colors have high RGB values
            return queryset.extra(
                where=["CAST(CONV(SUBSTRING(color, 2, 2), 16, 10) AS UNSIGNED) + "
                      "CAST(CONV(SUBSTRING(color, 4, 2), 16, 10) AS UNSIGNED) + "
                      "CAST(CONV(SUBSTRING(color, 6, 2), 16, 10) AS UNSIGNED) > 600"]
            )
        elif value == 'dark':
            # Dark colors have low RGB values
            return queryset.extra(
                where=["CAST(CONV(SUBSTRING(color, 2, 2), 16, 10) AS UNSIGNED) + "
                      "CAST(CONV(SUBSTRING(color, 4, 2), 16, 10) AS UNSIGNED) + "
                      "CAST(CONV(SUBSTRING(color, 6, 2), 16, 10) AS UNSIGNED) < 200"]
            )
        elif value == 'bright':
            # Bright colors have medium to high RGB values
            return queryset.extra(
                where=["CAST(CONV(SUBSTRING(color, 2, 2), 16, 10) AS UNSIGNED) + "
                      "CAST(CONV(SUBSTRING(color, 4, 2), 16, 10) AS UNSIGNED) + "
                      "CAST(CONV(SUBSTRING(color, 6, 2), 16, 10) AS UNSIGNED) BETWEEN 200 AND 600"]
            )
        return queryset


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

    class GraphQLMeta(GraphQLMeta):
        """GraphQL configuration for Post model - Enhanced with comprehensive features."""
        
        # Quick filter configuration - search across multiple fields
        quick_filter_fields = [
            'title',
            'content', 
            'excerpt',
            'author__username',
            'author__first_name',
            'author__last_name',
            'category__name',
            'tags__name'
        ]
        
        # Custom resolvers for specialized queries
        custom_resolvers = {
            'published_posts': 'get_published_posts',
            'featured_posts': 'get_featured_posts',
            'popular_posts': 'get_popular_posts',
            'recent_posts': 'get_recent_posts',
            'author_posts': 'get_posts_by_author',
            'trending_posts': 'get_trending_posts',
            'draft_posts': 'get_draft_posts',
        }
        
        # Custom filters for advanced filtering
        custom_filters = {
            'has_comments': 'filter_has_comments',
            'content_length': 'filter_by_content_length',
            'tag_count': 'filter_by_tag_count',
            'published_this_year': 'filter_published_this_year',
            'engagement_level': 'filter_by_engagement_level',
            'reading_time': 'filter_by_reading_time',
        }
        
        # Standard filter fields
        filter_fields = {
            'title': ['exact', 'icontains', 'startswith'],
            'status': ['exact', 'in'],
            'is_featured': ['exact'],
            'created_at': ['exact', 'gt', 'gte', 'lt', 'lte', 'range'],
            'updated_at': ['exact', 'gt', 'gte', 'lt', 'lte', 'range'],
            'published_at': ['exact', 'gt', 'gte', 'lt', 'lte', 'range'],
            'author': ['exact'],
            'category': ['exact', 'in'],
            'tags': ['exact', 'in'],
            'view_count': ['exact', 'gt', 'gte', 'lt', 'lte', 'range'],
            'quick': ['icontains'],  # Enable quick filter
        }
        
        # Ordering fields
        ordering_fields = ['title', 'created_at', 'updated_at', 'published_at', 'view_count']

    def __str__(self):
        return self.title

    def test_prop(self) -> date:
        return self.created_at

    # Custom resolver methods for GraphQLMeta
    @classmethod
    def get_published_posts(cls, queryset, info, **kwargs):
        """Get only published posts."""
        return queryset.filter(status='published')

    @classmethod
    def get_featured_posts(cls, queryset, info, **kwargs):
        """Get featured posts that are published."""
        return queryset.filter(is_featured=True, status='published')

    @classmethod
    def get_popular_posts(cls, queryset, info, **kwargs):
        """Get posts with high view count."""
        return queryset.filter(
            status='published',
            view_count__gte=100
        ).order_by('-view_count')

    @classmethod
    def get_recent_posts(cls, queryset, info, days=7, **kwargs):
        """Get posts from the last N days."""
        cutoff_date = timezone.now() - timedelta(days=days)
        return queryset.filter(
            status='published',
            published_at__gte=cutoff_date
        ).order_by('-published_at')

    @classmethod
    def get_posts_by_author(cls, queryset, info, author_id=None, **kwargs):
        """Get posts by specific author."""
        if author_id:
            return queryset.filter(author_id=author_id, status='published')
        return queryset.filter(status='published')

    @classmethod
    def get_trending_posts(cls, queryset, info, **kwargs):
        """Get trending posts based on recent views and comments."""
        seven_days_ago = timezone.now() - timedelta(days=7)
        return queryset.filter(
            status='published',
            published_at__gte=seven_days_ago
        ).annotate(
            comment_count=Count('comments')
        ).filter(
            Q(view_count__gte=50) | Q(comment_count__gte=5)
        ).order_by('-view_count', '-comment_count')

    @classmethod
    def get_draft_posts(cls, queryset, info, **kwargs):
        """Get draft posts (requires appropriate permissions)."""
        return queryset.filter(status='draft')

    # Custom filter methods for GraphQLMeta
    @classmethod
    def filter_has_comments(cls, queryset, name, value):
        """Filter posts that have or don't have comments."""
        if value:
            return queryset.filter(comments__isnull=False).distinct()
        return queryset.filter(comments__isnull=True)

    @classmethod
    def filter_by_content_length(cls, queryset, name, value):
        """Filter by content length (short, medium, long)."""
        if value == 'short':
            return queryset.extra(where=["LENGTH(content) < 500"])
        elif value == 'medium':
            return queryset.extra(where=["LENGTH(content) BETWEEN 500 AND 2000"])
        elif value == 'long':
            return queryset.extra(where=["LENGTH(content) > 2000"])
        return queryset

    @classmethod
    def filter_by_tag_count(cls, queryset, name, value):
        """Filter by number of tags."""
        return queryset.annotate(
            tag_count=Count('tags')
        ).filter(tag_count=value)

    @classmethod
    def filter_published_this_year(cls, queryset, name, value):
        """Filter posts published this year."""
        if value:
            current_year = timezone.now().year
            return queryset.filter(
                published_at__year=current_year,
                status='published'
            )
        return queryset

    @classmethod
    def filter_by_engagement_level(cls, queryset, name, value):
        """Filter by engagement level (high, medium, low)."""
        queryset = queryset.annotate(
            comment_count=Count('comments')
        )
        
        if value == 'high':
            return queryset.filter(
                Q(view_count__gte=200) | Q(comment_count__gte=10)
            )
        elif value == 'medium':
            return queryset.filter(
                Q(view_count__range=(50, 199)) | Q(comment_count__range=(3, 9))
            )
        elif value == 'low':
            return queryset.filter(
                view_count__lt=50,
                comment_count__lt=3
            )
        return queryset

    @classmethod
    def filter_by_reading_time(cls, queryset, name, value):
        """Filter by estimated reading time (quick, medium, long)."""
        # Assuming average reading speed of 200 words per minute
        # and roughly 5 characters per word
        if value == 'quick':
            # Less than 3 minutes (600 words, ~3000 characters)
            return queryset.extra(where=["LENGTH(content) < 3000"])
        elif value == 'medium':
            # 3-10 minutes (600-2000 words, ~3000-10000 characters)
            return queryset.extra(where=["LENGTH(content) BETWEEN 3000 AND 10000"])
        elif value == 'long':
            # More than 10 minutes (2000+ words, ~10000+ characters)
            return queryset.extra(where=["LENGTH(content) > 10000"])
        return queryset

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

    class GraphQLMeta(GraphQLMeta):
        """GraphQL configuration for Comment model."""
        
        # Quick filter configuration - search across comment fields
        quick_filter_fields = [
            'content',
            'author__username',
            'author__first_name',
            'author__last_name',
            'post__title',
        ]
        
        # Custom resolvers for specialized queries
        custom_resolvers = {
            'approved_comments': 'get_approved_comments',
            'pending_comments': 'get_pending_comments',
            'flagged_comments': 'get_flagged_comments',
            'recent_comments': 'get_recent_comments',
            'top_level_comments': 'get_top_level_comments',
            'replies': 'get_replies',
        }
        
        # Custom filters for advanced filtering
        custom_filters = {
            'has_replies': 'filter_has_replies',
            'content_length': 'filter_by_content_length',
            'author_activity': 'filter_by_author_activity',
        }
        
        # Standard filter fields
        filter_fields = {
            'content': ['icontains'],
            'is_approved': ['exact'],
            'is_flagged': ['exact'],
            'created_at': ['exact', 'gt', 'gte', 'lt', 'lte', 'range'],
            'updated_at': ['exact', 'gt', 'gte', 'lt', 'lte', 'range'],
            'author': ['exact'],
            'post': ['exact'],
            'parent': ['exact', 'isnull'],
            'quick': ['icontains'],  # Enable quick filter
        }
        
        # Ordering fields
        ordering_fields = ['created_at', 'updated_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"

    # Custom resolver methods for GraphQLMeta
    @classmethod
    def get_approved_comments(cls, queryset, info, **kwargs):
        """Get only approved comments."""
        return queryset.filter(is_approved=True, is_flagged=False)

    @classmethod
    def get_pending_comments(cls, queryset, info, **kwargs):
        """Get comments pending approval."""
        return queryset.filter(is_approved=False, is_flagged=False)

    @classmethod
    def get_flagged_comments(cls, queryset, info, **kwargs):
        """Get flagged comments (admin only)."""
        return queryset.filter(is_flagged=True)

    @classmethod
    def get_recent_comments(cls, queryset, info, days=7, **kwargs):
        """Get comments from the last N days."""
        cutoff_date = timezone.now() - timedelta(days=days)
        return queryset.filter(
            created_at__gte=cutoff_date,
            is_approved=True
        ).order_by('-created_at')

    @classmethod
    def get_top_level_comments(cls, queryset, info, **kwargs):
        """Get top-level comments (not replies)."""
        return queryset.filter(parent__isnull=True)

    @classmethod
    def get_replies(cls, queryset, info, **kwargs):
        """Get reply comments."""
        return queryset.filter(parent__isnull=False)

    # Custom filter methods for GraphQLMeta
    @classmethod
    def filter_has_replies(cls, queryset, name, value):
        """Filter comments that have or don't have replies."""
        if value:
            return queryset.filter(replies__isnull=False).distinct()
        return queryset.filter(replies__isnull=True)

    @classmethod
    def filter_by_content_length(cls, queryset, name, value):
        """Filter by content length (short, medium, long)."""
        if value == 'short':
            return queryset.extra(where=["LENGTH(content) < 100"])
        elif value == 'medium':
            return queryset.extra(where=["LENGTH(content) BETWEEN 100 AND 500"])
        elif value == 'long':
            return queryset.extra(where=["LENGTH(content) > 500"])
        return queryset

    @classmethod
    def filter_by_author_activity(cls, queryset, name, value):
        """Filter by author's comment activity level."""
        if value == 'active':
            # Authors with 5+ comments
            return queryset.annotate(
                author_comment_count=Count('author__comments')
            ).filter(author_comment_count__gte=5)
        elif value == 'new':
            # Authors with 1-2 comments
            return queryset.annotate(
                author_comment_count=Count('author__comments')
            ).filter(author_comment_count__lte=2)
        return queryset


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

    class GraphQLMeta(GraphQLMeta):
        """GraphQL configuration for Subscriber model."""
        
        # Quick filter configuration - search across subscriber fields
        quick_filter_fields = [
            'name',
            'email',  # Note: This should be restricted based on permissions
        ]
        
        # Custom resolvers for specialized queries
        custom_resolvers = {
            'active_subscribers': 'get_active_subscribers',
            'recent_subscribers': 'get_recent_subscribers',
            'unsubscribed_users': 'get_unsubscribed_users',
        }
        
        # Custom filters for advanced filtering
        custom_filters = {
            'subscription_duration': 'filter_by_subscription_duration',
            'has_preferences': 'filter_has_preferences',
        }
        
        # Standard filter fields
        filter_fields = {
            'name': ['exact', 'icontains', 'startswith'],
            'is_active': ['exact'],
            'subscribed_at': ['exact', 'gt', 'gte', 'lt', 'lte', 'range'],
            'unsubscribed_at': ['exact', 'gt', 'gte', 'lt', 'lte', 'isnull'],
            'quick': ['icontains'],  # Enable quick filter
        }
        
        # Ordering fields
        ordering_fields = ['name', 'subscribed_at', 'unsubscribed_at']

    def __str__(self):
        return f"Subscriber: {self.email}"

    # Custom resolver methods for GraphQLMeta
    @classmethod
    def get_active_subscribers(cls, queryset, info, **kwargs):
        """Get only active subscribers."""
        return queryset.filter(is_active=True, unsubscribed_at__isnull=True)

    @classmethod
    def get_recent_subscribers(cls, queryset, info, days=30, **kwargs):
        """Get subscribers from the last N days."""
        cutoff_date = timezone.now() - timedelta(days=days)
        return queryset.filter(
            subscribed_at__gte=cutoff_date,
            is_active=True
        ).order_by('-subscribed_at')

    @classmethod
    def get_unsubscribed_users(cls, queryset, info, **kwargs):
        """Get unsubscribed users."""
        return queryset.filter(
            Q(is_active=False) | Q(unsubscribed_at__isnull=False)
        )

    # Custom filter methods for GraphQLMeta
    @classmethod
    def filter_by_subscription_duration(cls, queryset, name, value):
        """Filter by how long they've been subscribed."""
        now = timezone.now()
        
        if value == 'new':
            # Subscribed within last 7 days
            cutoff = now - timedelta(days=7)
            return queryset.filter(subscribed_at__gte=cutoff)
        elif value == 'regular':
            # Subscribed 7-90 days ago
            start = now - timedelta(days=90)
            end = now - timedelta(days=7)
            return queryset.filter(subscribed_at__range=(start, end))
        elif value == 'loyal':
            # Subscribed more than 90 days ago
            cutoff = now - timedelta(days=90)
            return queryset.filter(subscribed_at__lt=cutoff)
        return queryset

    @classmethod
    def filter_has_preferences(cls, queryset, name, value):
        """Filter subscribers with or without preferences."""
        if value:
            return queryset.exclude(preferences={})
        return queryset.filter(preferences={})


@secure_model({
    'required_roles': [BlogRoles.ADMIN],
    'audit_operations': ['create', 'update', 'delete'],
    'field_permissions': {
        'maintenance_mode': FieldAccessLevel.ADMIN_ONLY,
        'api_keys': FieldAccessLevel.ADMIN_ONLY,
    }
})
class BlogSettings(models.Model):
    """Global blog settings and configuration."""
    site_title = models.CharField(max_length=200, default="My Blog")
    site_description = models.TextField(blank=True)
    posts_per_page = models.PositiveIntegerField(default=10)
    allow_comments = models.BooleanField(default=True)
    moderate_comments = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class GraphQLMeta(GraphQLMeta):
        """GraphQL configuration for BlogSettings model."""
        
        # Quick filter configuration - search across settings
        quick_filter_fields = [
            'site_title',
            'site_description',
        ]
        
        # Custom resolvers for specialized queries
        custom_resolvers = {
            'public_settings': 'get_public_settings',
            'admin_settings': 'get_admin_settings',
            'comment_settings': 'get_comment_settings',
        }
        
        # Custom filters for advanced filtering
        custom_filters = {
            'setting_type': 'filter_by_setting_type',
            'is_default': 'filter_is_default',
        }
        
        # Standard filter fields
        filter_fields = {
            'site_title': ['exact', 'icontains'],
            'allow_comments': ['exact'],
            'moderate_comments': ['exact'],
            'maintenance_mode': ['exact'],
            'posts_per_page': ['exact', 'gt', 'gte', 'lt', 'lte'],
            'created_at': ['exact', 'gt', 'gte', 'lt', 'lte', 'range'],
            'updated_at': ['exact', 'gt', 'gte', 'lt', 'lte', 'range'],
            'quick': ['icontains'],  # Enable quick filter
        }
        
        # Ordering fields
        ordering_fields = ['site_title', 'created_at', 'updated_at', 'posts_per_page']

    class Meta:
        verbose_name = "Blog Settings"
        verbose_name_plural = "Blog Settings"

    def __str__(self):
        return f"Blog Settings: {self.site_title}"

    # Custom resolver methods for GraphQLMeta
    @classmethod
    def get_public_settings(cls, queryset, info, **kwargs):
        """Get settings that are safe to expose publicly."""
        # Return settings excluding sensitive fields
        return queryset.values(
            'site_title', 'site_description', 'posts_per_page',
            'allow_comments', 'moderate_comments'
        )

    @classmethod
    def get_admin_settings(cls, queryset, info, **kwargs):
        """Get all settings (admin only)."""
        # This should be restricted by permissions in the GraphQL layer
        return queryset

    @classmethod
    def get_comment_settings(cls, queryset, info, **kwargs):
        """Get comment-related settings."""
        return queryset.values('allow_comments', 'moderate_comments')

    # Custom filter methods for GraphQLMeta
    @classmethod
    def filter_by_setting_type(cls, queryset, name, value):
        """Filter settings by type/category."""
        if value == 'display':
            # Settings related to display/appearance
            return queryset.filter(
                Q(site_title__isnull=False) | 
                Q(site_description__isnull=False) |
                Q(posts_per_page__gt=0)
            )
        elif value == 'comments':
            # Comment-related settings
            return queryset.filter(
                Q(allow_comments=True) | Q(moderate_comments=True)
            )
        elif value == 'system':
            # System/admin settings
            return queryset.filter(maintenance_mode=True)
        return queryset

    @classmethod
    def filter_is_default(cls, queryset, name, value):
        """Filter settings that have default values."""
        if value:
            return queryset.filter(
                site_title="My Blog",
                posts_per_page=10,
                allow_comments=True,
                moderate_comments=True,
                maintenance_mode=False
            )
        return queryset.exclude(
            site_title="My Blog",
            posts_per_page=10,
            allow_comments=True,
            moderate_comments=True,
            maintenance_mode=False
        )

    def save(self, *args, **kwargs):
        # Ensure only one settings instance exists
        if not self.pk and BlogSettings.objects.exists():
            raise ValueError("Only one BlogSettings instance is allowed")
        super().save(*args, **kwargs)
