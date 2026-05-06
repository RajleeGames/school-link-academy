from django.urls import path
from . import views

urlpatterns = [
    path("", views.academics_home, name="academics_home"),

    path("academic-years/", views.academic_year_list, name="academic_year_list"),
    path("terms/", views.term_list, name="term_list"),
    path("classes/", views.class_level_list, name="class_level_list"),
    path("streams/", views.stream_list, name="stream_list"),
    path("subjects/", views.subject_list, name="subject_list"),

    path("academic-years/create/", views.academic_year_create, name="academic_year_create"),
    path("terms/create/", views.term_create, name="term_create"),
    path("classes/create/", views.class_level_create, name="class_level_create"),
    path("streams/create/", views.stream_create, name="stream_create"),
    path("subjects/create/", views.subject_create, name="subject_create"),

    path("academic-years/<int:pk>/edit/", views.academic_year_update, name="academic_year_update"),
    path("terms/<int:pk>/edit/", views.term_update, name="term_update"),
    path("classes/<int:pk>/edit/", views.class_level_update, name="class_level_update"),
    path("streams/<int:pk>/edit/", views.stream_update, name="stream_update"),
    path("subjects/<int:pk>/edit/", views.subject_update, name="subject_update"),

    path("academic-years/<int:pk>/delete/", views.academic_year_delete, name="academic_year_delete"),
    path("terms/<int:pk>/delete/", views.term_delete, name="term_delete"),
    path("classes/<int:pk>/delete/", views.class_level_delete, name="class_level_delete"),
    path("streams/<int:pk>/delete/", views.stream_delete, name="stream_delete"),
    path("subjects/<int:pk>/delete/", views.subject_delete, name="subject_delete"),
]