from django.urls import path
from . import views

urlpatterns = [
    path("", views.expenses_home, name="expenses_home"),

    path("categories/", views.expense_category_list, name="expense_category_list"),
    path("categories/<int:pk>/edit/", views.expense_category_update, name="expense_category_update"),
    path("categories/<int:pk>/delete/", views.expense_category_delete, name="expense_category_delete"),

    path("list/", views.expense_list, name="expense_list"),
    path("create/", views.expense_create, name="expense_create"),
    path("<int:pk>/", views.expense_detail, name="expense_detail"),
    path("<int:pk>/edit/", views.expense_update, name="expense_update"),
    path("<int:pk>/delete/", views.expense_delete, name="expense_delete"),
]