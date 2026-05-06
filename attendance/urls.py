from django.urls import path
from . import views

urlpatterns = [
    path("", views.attendance_home, name="attendance_home"),

    path("daily-register/", views.daily_register, name="daily_register"),

    path("students/", views.student_attendance_list, name="student_attendance_list"),
    path("students/mark/", views.student_attendance_create, name="student_attendance_create"),
    path("students/bulk/", views.bulk_student_attendance, name="bulk_student_attendance"),
    path("students/<int:pk>/edit/", views.student_attendance_update, name="student_attendance_update"),
    path("students/<int:pk>/delete/", views.student_attendance_delete, name="student_attendance_delete"),

    path("staff/", views.staff_attendance_list, name="staff_attendance_list"),
    path("staff/mark/", views.staff_attendance_create, name="staff_attendance_create"),
    path("staff/<int:pk>/edit/", views.staff_attendance_update, name="staff_attendance_update"),
    path("staff/<int:pk>/delete/", views.staff_attendance_delete, name="staff_attendance_delete"),
]