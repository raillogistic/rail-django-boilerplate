from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model extending Django's AbstractUser."""
    # Add custom fields here if needed
    bio = models.TextField(blank=True, default='')

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    """User profile model with OneToOne relationship to User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, help_text="User biography")
    birth_date = models.DateField(null=True, blank=True, help_text="User birth date")
    phone_number = models.CharField(max_length=20, blank=True, help_text="User phone number")
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f"Profile for {self.user.username}"