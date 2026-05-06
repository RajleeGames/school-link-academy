from django.contrib import admin
from .models import ExamType, Exam, GradeScale, ExamResult


@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "exam_type",
        "academic_year",
        "term",
        "class_level",
        "start_date",
        "end_date",
        "status",
        "is_active",
    )
    search_fields = ("name",)
    list_filter = (
        "exam_type",
        "academic_year",
        "term",
        "class_level",
        "status",
        "is_active",
    )


@admin.register(GradeScale)
class GradeScaleAdmin(admin.ModelAdmin):
    list_display = ("grade", "min_score", "max_score", "points", "remark", "is_active")
    list_filter = ("is_active",)
    search_fields = ("grade", "remark")


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = (
        "exam",
        "student",
        "subject",
        "marks",
        "grade",
        "points",
        "remark",
    )
    search_fields = (
        "exam__name",
        "student__admission_number",
        "student__first_name",
        "student__last_name",
        "subject__name",
    )
    list_filter = (
        "exam",
        "subject",
        "grade",
        "exam__class_level",
    )