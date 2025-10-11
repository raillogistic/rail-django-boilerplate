"""
Core models for the Django GraphQL application.

This module contains models that are used across multiple extensions
to avoid AppRegistryNotReady errors when importing from extensions.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone as django_timezone
from django.core.validators import MinLengthValidator
import uuid


class AuditEventModel(models.Model):
    """
    Modèle Django pour stocker les événements d'audit en base de données.
    """
    event_type = models.CharField(max_length=50, db_index=True)
    severity = models.CharField(max_length=20, db_index=True)
    user_id = models.IntegerField(null=True, blank=True, db_index=True)
    username = models.CharField(max_length=150, null=True, blank=True, db_index=True)
    client_ip = models.GenericIPAddressField(db_index=True)
    user_agent = models.TextField()
    timestamp = models.DateTimeField(default=django_timezone.now, db_index=True)
    request_path = models.CharField(max_length=500)
    request_method = models.CharField(max_length=10)
    additional_data = models.JSONField(null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    success = models.BooleanField(default=True, db_index=True)
    error_message = models.TextField(null=True, blank=True)
    
    class Meta:
        app_label = 'core'
        db_table = 'audit_events'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['user_id', 'timestamp']),
            models.Index(fields=['severity', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.username or 'Anonymous'} - {self.timestamp}"


class MFADevice(models.Model):
    """
    Modèle pour les dispositifs d'authentification multi-facteurs.
    """
    DEVICE_TYPES = [
        ('totp', 'TOTP (Time-based One-Time Password)'),
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('backup', 'Backup Codes'),
    ]
    
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='mfa_devices'
    )
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES)
    name = models.CharField(max_length=100, help_text="Nom donné par l'utilisateur")
    secret_key = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'core'
        db_table = 'mfa_devices'
        unique_together = ['user', 'device_type', 'name']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_device_type_display()} - {self.name}"


class MFABackupCode(models.Model):
    """
    Modèle pour les codes de sauvegarde MFA.
    """
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='mfa_backup_codes'
    )
    code = models.CharField(
        max_length=10,
        validators=[MinLengthValidator(8)],
        help_text="Code de sauvegarde à 8-10 caractères"
    )
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'core'
        db_table = 'mfa_backup_codes'
        unique_together = ['user', 'code']
    
    def __str__(self):
        return f"{self.user.username} - Backup Code ({'Used' if self.is_used else 'Active'})"


class TrustedDevice(models.Model):
    """
    Modèle pour les appareils de confiance qui peuvent contourner MFA.
    """
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='trusted_devices'
    )
    device_fingerprint = models.CharField(
        max_length=255,
        unique=True,
        help_text="Empreinte unique de l'appareil"
    )
    device_name = models.CharField(max_length=100, blank=True)
    user_agent = models.TextField()
    ip_address = models.GenericIPAddressField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(
        help_text="Date d'expiration de la confiance"
    )
    
    class Meta:
        app_label = 'core'
        db_table = 'trusted_devices'
        unique_together = ['user', 'device_fingerprint']
    
    def __str__(self):
        return f"{self.user.username} - {self.device_name or 'Unknown Device'}"
    
    @property
    def is_expired(self):
        """Vérifie si l'appareil de confiance a expiré."""
        return django_timezone.now() > self.expires_at