from django.urls import path
from . import views

urlpatterns = [
    path("", views.reports_home, name="reports_home"),

    path("students/", views.student_report, name="student_report"),
    path("fees/", views.fees_report, name="fees_report"),
    path("expenses/", views.expenses_report, name="expenses_report"),
    path("attendance/", views.attendance_report, name="attendance_report"),

    path("students/export/excel/", views.export_student_report_excel, name="export_student_report_excel"),
    path("fees/export/excel/", views.export_fees_report_excel, name="export_fees_report_excel"),
    path("expenses/export/excel/", views.export_expenses_report_excel, name="export_expenses_report_excel"),
    path("attendance/export/excel/", views.export_attendance_report_excel, name="export_attendance_report_excel"),
]