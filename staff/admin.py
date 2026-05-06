from django.contrib import admin
from .models import StaffProfile


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = (
        "staff_id",
        "full_name",
        "role",
        "gender",
        "phone",
        "email",
        "status",
    )
    search_fields = (
        "staff_id",
        "first_name",
        "middle_name",
        "last_name",
        "phone",
        "email",
    )
    list_filter = ("role", "gender", "status")
    filter_horizontal = ("assigned_classes", "subjects")