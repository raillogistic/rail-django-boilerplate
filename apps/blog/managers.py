from django.db import models


# write custom manager for published posts
class PublishedManager(models.Manager):
    """Custom manager for published posts."""

    def get_queryset(self):
        return super().get_queryset().filter(status="published")
