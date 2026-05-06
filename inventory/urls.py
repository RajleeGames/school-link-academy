from django.urls import path

from . import views


urlpatterns = [
    path("", views.inventory_home, name="inventory_home"),

    path("items/", views.item_list, name="inventory_item_list"),
    path("items/create/", views.item_create, name="inventory_item_create"),
    path("items/<int:pk>/edit/", views.item_update, name="inventory_item_update"),
    path("items/<int:pk>/delete/", views.item_delete, name="inventory_item_delete"),

    path("categories/", views.category_list, name="inventory_category_list"),
    path("categories/create/", views.category_create, name="inventory_category_create"),
    path("categories/<int:pk>/edit/", views.category_update, name="inventory_category_update"),
    path("categories/<int:pk>/delete/", views.category_delete, name="inventory_category_delete"),

    path("suppliers/", views.supplier_list, name="supplier_list"),
    path("suppliers/create/", views.supplier_create, name="supplier_create"),
    path("suppliers/<int:pk>/edit/", views.supplier_update, name="supplier_update"),
    path("suppliers/<int:pk>/delete/", views.supplier_delete, name="supplier_delete"),

    path("stock-in/", views.stock_in_list, name="stock_in_list"),
    path("stock-in/create/", views.stock_in_create, name="stock_in_create"),
    path("stock-in/<int:pk>/edit/", views.stock_in_update, name="stock_in_update"),
    path("stock-in/<int:pk>/delete/", views.stock_in_delete, name="stock_in_delete"),

    path("stock-out/", views.stock_out_list, name="stock_out_list"),
    path("stock-out/create/", views.stock_out_create, name="stock_out_create"),
    path("stock-out/<int:pk>/edit/", views.stock_out_update, name="stock_out_update"),
    path("stock-out/<int:pk>/delete/", views.stock_out_delete, name="stock_out_delete"),
]