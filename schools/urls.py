from django.urls import path

from . import views

urlpatterns = [
    path("profile/", views.school_profile, name="school_profile"),

    path("branches/", views.school_branch_list, name="school_branch_list"),
    path("branches/add/", views.school_branch_create, name="school_branch_create"),
    path("branches/<int:pk>/edit/", views.school_branch_update, name="school_branch_update"),

    path("settings/", views.system_settings, name="system_settings"),

    path("permissions/", views.user_permissions, name="user_permissions"),
    path("permissions/<int:pk>/edit/", views.user_permission_update, name="user_permission_update"),
]