from django.urls import path
from . import views

urlpatterns = [
    path("", views.student_list, name="student_list"),
    path("add/", views.student_create, name="student_create"),
    path("<int:pk>/", views.student_detail, name="student_detail"),
    path("<int:pk>/edit/", views.student_update, name="student_update"),

    path("admissions/", views.admission_list, name="admission_list"),

    path("parents/", views.parent_list, name="parent_list"),
    path("parents/add/", views.parent_create, name="parent_create"),
    path("parents/<int:pk>/edit/", views.parent_update, name="parent_update"),
]