from django.contrib import admin

from .models import SchoolBranch, SchoolProfile, SystemSetting


@admin.register(SchoolProfile)
class SchoolProfileAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "school_type",
        "school_mode",
        "phone",
        "email",
        "is_active",
    )
    search_fields = ("name", "phone", "email", "registration_number")
    list_filter = ("school_type", "school_mode", "is_active")


@admin.register(SchoolBranch)
class SchoolBranchAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "phone",
        "manager_name",
        "is_main_branch",
        "is_active",
    )
    search_fields = ("name", "code", "phone", "manager_name")
    list_filter = ("is_main_branch", "is_active")


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = (
        "default_currency",
        "attendance_mode",
        "enable_sms_notifications",
        "enable_parent_portal",
        "enable_student_portal",
    )