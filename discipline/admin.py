from django.contrib import admin
from .models import DisciplineCategory, DisciplineRecord, DisciplineFollowUp


class DisciplineFollowUpInline(admin.TabularInline):
    model = DisciplineFollowUp
    extra = 0


@admin.register(DisciplineCategory)
class DisciplineCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category_type", "is_active")
    list_filter = ("category_type", "is_active")
    search_fields = ("name", "description")


@admin.register(DisciplineRecord)
class DisciplineRecordAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "record_type",
        "category",
        "title",
        "incident_date",
        "severity",
        "parent_notified",
        "status",
    )
    list_filter = (
        "record_type",
        "category",
        "severity",
        "status",
        "parent_notified",
        "incident_date",
    )
    search_fields = (
        "student__admission_number",
        "student__first_name",
        "student__last_name",
        "title",
        "description",
        "action_taken",
    )
    inlines = [DisciplineFollowUpInline]


@admin.register(DisciplineFollowUp)
class DisciplineFollowUpAdmin(admin.ModelAdmin):
    list_display = ("record", "follow_up_date", "handled_by", "next_action")
    list_filter = ("follow_up_date",)
    search_fields = ("record__title", "note", "next_action")