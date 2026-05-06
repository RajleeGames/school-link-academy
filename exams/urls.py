from django.urls import path
from . import views

urlpatterns = [
    path("", views.exams_home, name="exams_home"),

    path("types/", views.exam_type_list, name="exam_type_list"),
    path("types/<int:pk>/edit/", views.exam_type_update, name="exam_type_update"),
    path("types/<int:pk>/delete/", views.exam_type_delete, name="exam_type_delete"),

    path("grades/", views.grade_scale_list, name="grade_scale_list"),
    path("grades/<int:pk>/edit/", views.grade_scale_update, name="grade_scale_update"),
    path("grades/<int:pk>/delete/", views.grade_scale_delete, name="grade_scale_delete"),

    path("list/", views.exam_list, name="exam_list"),
    path("create/", views.exam_create, name="exam_create"),
    path("<int:pk>/", views.exam_detail, name="exam_detail"),
    path("<int:pk>/edit/", views.exam_update, name="exam_update"),
    path("<int:pk>/delete/", views.exam_delete, name="exam_delete"),

    path("results/", views.result_list, name="result_list"),
    path("results/create/", views.result_create, name="result_create"),
    path("results/<int:pk>/edit/", views.result_update, name="result_update"),
    path("results/<int:pk>/delete/", views.result_delete, name="result_delete"),
    path("results/bulk/", views.bulk_marks_entry, name="bulk_marks_entry"),

    path("performance/", views.class_performance_report, name="class_performance_report"),

    path("report-card/<int:student_id>/", views.student_report_card, name="student_report_card"),

    path("results/export/excel/", views.export_results_excel, name="export_results_excel"),
    path("performance/export/excel/", views.export_class_performance_excel, name="export_class_performance_excel"),
]