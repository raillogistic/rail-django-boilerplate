"""
URL configuration for django-graphql-boilerplate project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from graphene_django.views import GraphQLView
from rail_django_graphql.health_urls import health_urlpatterns
from rail_django_graphql.views.graphql_views import (
    GraphQLPlaygroundView,
    MultiSchemaGraphQLView,
    SchemaListView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    # GraphQL endpoint (library view)
    path(
        "graphql/",
        csrf_exempt(
            GraphQLView.as_view(
                graphiql=settings.RAIL_DJANGO_GRAPHQL["SECURITY"].get(
                    "ENABLE_GRAPHIQL", False
                )
            )
        ),
    ),
    # Health check endpoints
    path("", include(health_urlpatterns)),
    # App URLs
    path("users/", include("apps.users.urls")),
    path("blog/", include("apps.blog.urls")),
    # Core multi-schema endpoint
    path(
        "graphql/<str:schema_name>/",
        MultiSchemaGraphQLView.as_view(),
        name="graphql-by-schema",
    ),
    # Optional: list all available schemas and basic metadata
    path("schemas/", SchemaListView.as_view(), name="graphql-schemas"),
    # Optional: per-schema Playground (respects schema setting for GraphiQL)
    path(
        "playground/<str:schema_name>/",
        GraphQLPlaygroundView.as_view(),
        name="graphql-playground",
    ),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
