from django.contrib import admin
from .models import StudentAttendance, StaffAttendance


@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "status", "arrival_time", "remarks")
    list_filter = ("date", "status", "student__class_level", "student__stream")
    search_fields = (
        "student__admission_number",
        "student__first_name",
        "student__middle_name",
        "student__last_name",
    )


@admin.register(StaffAttendance)
class StaffAttendanceAdmin(admin.ModelAdmin):
    list_display = ("staff", "date", "status", "check_in_time", "check_out_time", "remarks")
    list_filter = ("date", "status", "staff__role")
    search_fields = (
        "staff__staff_id",
        "staff__first_name",
        "staff__middle_name",
        "staff__last_name",
    )