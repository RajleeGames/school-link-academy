from django.urls import path
from . import views

urlpatterns = [
    path("", views.homework_home, name="homework_home"),

    path("list/", views.homework_list, name="homework_list"),
    path("create/", views.homework_create, name="homework_create"),
    path("<int:pk>/", views.homework_detail, name="homework_detail"),
    path("<int:pk>/edit/", views.homework_update, name="homework_update"),
    path("<int:pk>/delete/", views.homework_delete, name="homework_delete"),
    path("<int:pk>/auto-submissions/", views.auto_create_homework_submissions, name="auto_create_homework_submissions"),

    path("submissions/", views.submission_list, name="submission_list"),
    path("submissions/create/", views.submission_create, name="submission_create"),
    path("submissions/<int:pk>/edit/", views.submission_update, name="submission_update"),
    path("submissions/<int:pk>/delete/", views.submission_delete, name="submission_delete"),
]