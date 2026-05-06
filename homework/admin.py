from django.contrib import admin
from .models import Homework, HomeworkSubmission


class HomeworkSubmissionInline(admin.TabularInline):
    model = HomeworkSubmission
    extra = 0


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "class_level",
        "stream",
        "subject",
        "teacher",
        "assigned_date",
        "due_date",
        "status",
        "is_active",
    )
    list_filter = (
        "academic_year",
        "term",
        "class_level",
        "stream",
        "subject",
        "status",
        "is_active",
    )
    search_fields = (
        "title",
        "description",
        "subject__name",
        "teacher__first_name",
        "teacher__last_name",
    )
    inlines = [HomeworkSubmissionInline]


@admin.register(HomeworkSubmission)
class HomeworkSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "homework",
        "student",
        "submitted_date",
        "marks",
        "status",
    )
    list_filter = (
        "homework",
        "status",
        "submitted_date",
    )
    search_fields = (
        "homework__title",
        "student__admission_number",
        "student__first_name",
        "student__last_name",
    )