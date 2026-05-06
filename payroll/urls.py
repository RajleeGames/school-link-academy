from django.urls import path

from . import views


urlpatterns = [
    path("", views.payroll_home, name="payroll_home"),

    path(
        "salary-structures/",
        views.salary_structure_list,
        name="salary_structure_list"
    ),
    path(
        "salary-structures/create/",
        views.salary_structure_create,
        name="salary_structure_create"
    ),
    path(
        "salary-structures/<int:pk>/edit/",
        views.salary_structure_update,
        name="salary_structure_update"
    ),
    path(
        "salary-structures/<int:pk>/delete/",
        views.salary_structure_delete,
        name="salary_structure_delete"
    ),

    path(
        "records/",
        views.payroll_record_list,
        name="payroll_record_list"
    ),
    path(
        "records/create/",
        views.payroll_record_create,
        name="payroll_record_create"
    ),
    path(
        "records/<int:pk>/",
        views.payroll_record_detail,
        name="payroll_record_detail"
    ),
    path(
        "records/<int:pk>/edit/",
        views.payroll_record_update,
        name="payroll_record_update"
    ),
    path(
        "records/<int:pk>/delete/",
        views.payroll_record_delete,
        name="payroll_record_delete"
    ),

    path(
        "generate/",
        views.payroll_generate,
        name="payroll_generate"
    ),
]