from django.contrib import admin
from .models import AcademicYear, Term, ClassLevel, Stream, Subject


class TermInline(admin.TabularInline):
    model = Term
    extra = 1


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "is_current")
    list_filter = ("is_current",)
    search_fields = ("name",)
    inlines = [TermInline]


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ("name", "academic_year", "start_date", "end_date", "is_current")
    list_filter = ("academic_year", "is_current")
    search_fields = ("name", "academic_year__name")


@admin.register(ClassLevel)
class ClassLevelAdmin(admin.ModelAdmin):
    list_display = ("name", "level_type", "order", "is_active")
    list_filter = ("level_type", "is_active")
    search_fields = ("name",)


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ("name", "class_level", "capacity", "is_active")
    list_filter = ("class_level", "is_active")
    search_fields = ("name", "class_level__name")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "subject_type", "is_active")
    list_filter = ("subject_type", "is_active", "class_levels")
    search_fields = ("name", "code")
    filter_horizontal = ("class_levels",)