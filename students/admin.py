from django.contrib import admin
from .models import ParentGuardian, Student


@admin.register(ParentGuardian)
class ParentGuardianAdmin(admin.ModelAdmin):
    list_display = ("full_name", "relationship", "phone", "alternative_phone", "email")
    search_fields = ("full_name", "phone", "alternative_phone", "email")
    list_filter = ("relationship",)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "admission_number",
        "full_name",
        "gender",
        "class_level",
        "stream",
        "parent_guardian",
        "boarding_status",
        "status",
    )
    search_fields = (
        "admission_number",
        "first_name",
        "middle_name",
        "last_name",
        "parent_guardian__full_name",
        "parent_guardian__phone",
    )
    list_filter = (
        "gender",
        "class_level",
        "stream",
        "boarding_status",
        "status",
    )
    autocomplete_fields = ("parent_guardian",)