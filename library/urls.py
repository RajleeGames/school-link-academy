from django.urls import path

from . import views


urlpatterns = [
    path("", views.library_home, name="library_home"),

    path("books/", views.book_list, name="book_list"),
    path("books/create/", views.book_create, name="book_create"),
    path("books/<int:pk>/edit/", views.book_update, name="book_update"),
    path("books/<int:pk>/delete/", views.book_delete, name="book_delete"),

    path("categories/", views.category_list, name="book_category_list"),
    path("categories/create/", views.category_create, name="book_category_create"),
    path("categories/<int:pk>/edit/", views.category_update, name="book_category_update"),
    path("categories/<int:pk>/delete/", views.category_delete, name="book_category_delete"),

    path("borrow/", views.borrow_list, name="borrow_list"),
    path("borrow/create/", views.borrow_create, name="borrow_create"),
    path("borrow/<int:pk>/", views.borrow_detail, name="borrow_detail"),
    path("borrow/<int:pk>/return/", views.borrow_return, name="borrow_return"),
    path("borrow/<int:pk>/delete/", views.borrow_delete, name="borrow_delete"),
]