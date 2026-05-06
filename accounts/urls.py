from django.urls import path

from . import views


urlpatterns = [
    path("login/", views.SchoolLoginView.as_view(), name="login"),
    path("logout/", views.SchoolLogoutView.as_view(), name="logout"),
    path("redirect/", views.account_redirect, name="account_redirect"),

    path("roles/", views.user_role_list, name="user_role_list"),
    path("roles/<int:pk>/edit/", views.user_role_update, name="user_role_update"),

    path("parent-portal/", views.parent_portal_home, name="parent_portal_home"),
    path("parent-portal/student/<int:student_id>/invoices/", views.parent_student_invoices, name="parent_student_invoices"),
    path("parent-portal/student/<int:student_id>/payments/", views.parent_student_payments, name="parent_student_payments"),
    path("parent-portal/student/<int:student_id>/results/", views.parent_student_results, name="parent_student_results"),
    path("parent-portal/student/<int:student_id>/attendance/", views.parent_student_attendance, name="parent_student_attendance"),

    path("parents/<int:pk>/create-login/", views.create_parent_login, name="create_parent_login"),
]