from django.conf import settings
from django.db import models
from django.utils import timezone


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("cancel", "Cancel"),
        ("login", "Login"),
        ("logout", "Logout"),
        ("view", "View"),
        ("export", "Export"),
        ("generate", "Generate"),
        ("approve", "Approve"),
        ("pay", "Pay"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )

    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    app_label = models.CharField(max_length=100, blank=True)
    model_name = models.CharField(max_length=120, blank=True)
    object_id = models.CharField(max_length=120, blank=True)
    object_repr = models.CharField(max_length=255, blank=True)

    message = models.TextField(blank=True)

    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["action"]),
            models.Index(fields=["app_label"]),
            models.Index(fields=["model_name"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        username = self.user.username if self.user else "System"
        return f"{username} {self.action} {self.object_repr or self.model_name}"