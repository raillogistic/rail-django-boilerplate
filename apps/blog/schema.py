# """GraphQL schema for the blog app with comprehensive security features."""

# import graphene
# from django.contrib.auth import get_user_model
# from django.core.exceptions import PermissionDenied
# from django.db import models
# from graphene_django import DjangoObjectType
# from graphene_django.filter import DjangoFilterConnectionField

# from .models import BlogSettings, Category, Comment, Post, Subscriber, Tag
# from .security import (
#     BlogRoles,
#     FieldAccessLevel,
#     audit_operation,
#     require_authentication,
#     require_role,
#     secure_resolver,
#     validate_input,
# )

# User = get_user_model()


# class CategoryType(DjangoObjectType):
#     class Meta:
#         model = Category
#         fields = "__all__"
#         filter_fields = ["name", "slug", "is_active"]
#         interfaces = (graphene.relay.Node,)


# class TagType(DjangoObjectType):
#     class Meta:
#         model = Tag
#         fields = "__all__"
#         filter_fields = ["name", "slug", "is_active"]
#         interfaces = (graphene.relay.Node,)


# class PostType(DjangoObjectType):
#     class Meta:
#         model = Post
#         fields = "__all__"
#         # Standard filter fields without the quick filter
#         filter_fields = {
#             "title": ["exact", "icontains", "startswith"],
#             "status": ["exact", "in"],
#             "is_featured": ["exact"],
#             "created_at": ["exact", "gt", "gte", "lt", "lte", "range"],
#             "updated_at": ["exact", "gt", "gte", "lt", "lte", "range"],
#             "published_at": ["exact", "gt", "gte", "lt", "lte", "range"],
#             "author": ["exact"],
#             "category": ["exact", "in"],
#             "tags": ["exact", "in"],
#             "view_count": ["exact", "gt", "gte", "lt", "lte", "range"],
#         }
#         interfaces = (graphene.relay.Node,)


# class CommentType(DjangoObjectType):
#     class Meta:
#         model = Comment
#         fields = "__all__"
#         filter_fields = {
#             "post": ["exact"],
#             "is_approved": ["exact"],
#             "is_flagged": ["exact"],
#         }
#         interfaces = (graphene.relay.Node,)


# class SubscriberType(DjangoObjectType):
#     class Meta:
#         model = Subscriber
#         fields = "__all__"
#         filter_fields = ["is_active"]
#         interfaces = (graphene.relay.Node,)


# class BlogSettingsType(DjangoObjectType):
#     class Meta:
#         model = BlogSettings
#         fields = "__all__"
#         interfaces = (graphene.relay.Node,)


# class Query(graphene.ObjectType):
#     # Categories
#     categories = DjangoFilterConnectionField(CategoryType)
#     category = graphene.relay.Node.Field(CategoryType)

#     # Tags
#     tags = DjangoFilterConnectionField(TagType)
#     tag = graphene.relay.Node.Field(TagType)

#     # Posts
#     posts = DjangoFilterConnectionField(PostType, quick=graphene.String())
#     post = graphene.relay.Node.Field(PostType)
#     featured_posts = DjangoFilterConnectionField(PostType)

#     # Comments
#     comments = DjangoFilterConnectionField(CommentType)
#     comment = graphene.relay.Node.Field(CommentType)

#     # Subscribers (Admin only)
#     subscribers = DjangoFilterConnectionField(SubscriberType)
#     subscriber = graphene.relay.Node.Field(SubscriberType)

#     # Blog Settings
#     blog_settings = graphene.Field(BlogSettingsType)

#     def resolve_posts(self, info, **kwargs):
#         """Resolve posts with security filtering and quick filter support."""
#         user = info.context.user
#         queryset = Post.objects.all()

#         # Anonymous users can only see published posts
#         if user.is_anonymous:
#             queryset = queryset.filter(status="published")

#         # Handle quick filter
#         quick_search = kwargs.get("quick")
#         if quick_search:
#             from django.db.models import Q

#             # Search across multiple fields
#             q_objects = Q()
#             search_fields = [
#                 "title__icontains",
#                 "content__icontains",
#                 "excerpt__icontains",
#                 "author__username__icontains",
#                 "author__first_name__icontains",
#                 "author__last_name__icontains",
#                 "category__name__icontains",
#                 "tags__name__icontains",
#             ]

#             for field in search_fields:
#                 q_objects |= Q(**{field: quick_search})

#             queryset = queryset.filter(q_objects).distinct()

#         return queryset

#     def resolve_comments(self, info, **kwargs):
#         """Resolve comments with security filtering."""
#         user = info.context.user
#         queryset = Comment.objects.all()

#         # Anonymous users can only see approved comments
#         if user.is_anonymous:
#             queryset = queryset.filter(is_approved=True)
#         # Staff can see all comments
#         elif not user.is_staff:
#             # Regular users can see approved comments and their own
#             queryset = queryset.filter(
#                 models.Q(is_approved=True) | models.Q(author=user)
#             )

#         return queryset

#     def resolve_subscribers(self, info, **kwargs):
#         """Resolve subscribers - admin only."""
#         user = info.context.user
#         if not user.is_staff and not user.is_superuser:
#             raise PermissionDenied("Admin access required")
#         return Subscriber.objects.all()

#     def resolve_blog_settings(self, info, **kwargs):
#         """Resolve blog settings - admin/editor only."""
#         user = info.context.user
#         if not user.is_staff and not user.is_superuser:
#             raise PermissionDenied("Admin/Editor access required")
#         return BlogSettings.objects.first()

#     def resolve_featured_posts(self, info, **kwargs):
#         """Resolve featured posts."""
#         return Post.objects.filter(is_featured=True, status="published")

#     @secure_resolver
#     @require_role([BlogRoles.ADMIN])
#     def resolve_blog_settings(self, info, **kwargs):
#         """Resolve blog settings - Admin only."""
#         settings, created = BlogSettings.objects.get_or_create()
#         return settings


# # Mutations
# class CreateCategoryInput(graphene.InputObjectType):
#     name = graphene.String(required=True)
#     slug = graphene.String(required=True)
#     description = graphene.String()


# class CreateCategory(graphene.Mutation):
#     class Arguments:
#         input = CreateCategoryInput(required=True)

#     category = graphene.Field(CategoryType)
#     success = graphene.Boolean()
#     errors = graphene.List(graphene.String)

#     @staticmethod
#     def mutate(root, info, input):
#         # Check authentication
#         user = info.context.user
#         if user.is_anonymous:
#             raise PermissionDenied("Authentication required")

#         # Check role permissions
#         if not user.is_staff and not user.is_superuser:
#             # Check if user has proper roles
#             user_roles = getattr(user, "roles", [])
#             allowed_roles = [BlogRoles.ADMIN.value, BlogRoles.EDITOR.value]
#             if not any(role in user_roles for role in allowed_roles):
#                 raise PermissionDenied("Admin/Editor role required")

#         # Validate required fields
#         if not input.get("name") or not input.get("slug"):
#             raise ValueError("Name and slug are required")

#         try:
#             category = Category.objects.create(**input)
#             return CreateCategory(category=category, success=True, errors=[])
#         except Exception as e:
#             return CreateCategory(category=None, success=False, errors=[str(e)])


# class CreatePostInput(graphene.InputObjectType):
#     title = graphene.String(required=True)
#     slug = graphene.String(required=True)
#     content = graphene.String()
#     excerpt = graphene.String()
#     category_id = graphene.ID()
#     tag_ids = graphene.List(graphene.ID)
#     status = graphene.String()
#     featured_image = graphene.String()


# class CreatePost(graphene.Mutation):
#     class Arguments:
#         input = CreatePostInput(required=True)

#     post = graphene.Field(PostType)
#     success = graphene.Boolean()
#     errors = graphene.List(graphene.String)

#     @staticmethod
#     def mutate(root, info, input):
#         # Check authentication
#         user = info.context.user
#         if user.is_anonymous:
#             return CreatePost(
#                 post=None, success=False, errors=["Authentication required"]
#             )

#         # Check role permissions (authors, editors, admins can create posts)
#         if not user.is_staff and not user.is_superuser:
#             # In a real app, you'd check for author role here
#             pass  # For now, any authenticated user can create posts

#         try:
#             # Validate required fields
#             if not input.get("title") or not input.get("title").strip():
#                 return CreatePost(
#                     post=None, success=False, errors=["Title is required"]
#                 )

#             tag_ids = input.pop("tag_ids", [])

#             post = Post.objects.create(author=info.context.user, **input)

#             if tag_ids:
#                 post.tags.set(tag_ids)

#             return CreatePost(post=post, success=True, errors=[])
#         except Exception as e:
#             return CreatePost(post=None, success=False, errors=[str(e)])


# class CreateComment(graphene.Mutation):
#     class Arguments:
#         post_id = graphene.ID(required=True)
#         content = graphene.String(required=True)
#         parent_id = graphene.ID()

#     comment = graphene.Field(CommentType)
#     success = graphene.Boolean()
#     errors = graphene.List(graphene.String)

#     @staticmethod
#     def mutate(root, info, post_id, content, parent_id=None):
#         # Check authentication
#         user = info.context.user
#         if user.is_anonymous:
#             return CreateComment(
#                 comment=None, success=False, errors=["Authentication required"]
#             )

#         # Validate content
#         if not content or not content.strip():
#             return CreateComment(
#                 comment=None, success=False, errors=["Content is required"]
#             )

#         try:
#             comment = Comment.objects.create(
#                 post_id=post_id,
#                 author=info.context.user,
#                 content=content,
#                 parent_id=parent_id,
#             )
#             return CreateComment(comment=comment, success=True, errors=[])
#         except Exception as e:
#             return CreateComment(comment=None, success=False, errors=[str(e)])


# class SubscribeNewsletter(graphene.Mutation):
#     class Arguments:
#         email = graphene.String(required=True)
#         name = graphene.String()

#     subscriber = graphene.Field(SubscriberType)
#     success = graphene.Boolean()
#     errors = graphene.List(graphene.String)

#     @staticmethod
#     def mutate(root, info, email, name=None):
#         # Validate email
#         if not email or not email.strip():
#             return SubscribeNewsletter(
#                 subscriber=None, success=False, errors=["Email is required"]
#             )

#         try:
#             subscriber, created = Subscriber.objects.get_or_create(
#                 email=email, defaults={"name": name or ""}
#             )
#             return SubscribeNewsletter(subscriber=subscriber, success=True, errors=[])
#         except Exception as e:
#             return SubscribeNewsletter(subscriber=None, success=False, errors=[str(e)])


# class Mutation(graphene.ObjectType):
#     create_category = CreateCategory.Field()
#     create_post = CreatePost.Field()
#     create_comment = CreateComment.Field()
#     subscribe_newsletter = SubscribeNewsletter.Field()


# # schema = graphene.Schema(query=Query, mutation=Mutation)
