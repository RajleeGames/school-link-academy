from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        "created_at",
        "user",
        "action",
        "app_label",
        "model_name",
        "object_repr",
        "ip_address",
    ]
    list_filter = [
        "action",
        "app_label",
        "model_name",
        "created_at",
    ]
    search_fields = [
        "user__username",
        "object_repr",
        "message",
        "ip_address",
    ]
    readonly_fields = [
        "user",
        "action",
        "app_label",
        "model_name",
        "object_id",
        "object_repr",
        "message",
        "old_values",
        "new_values",
        "ip_address",
        "user_agent",
        "created_at",
    ]

    def has_add_permission(self, request):
        return False