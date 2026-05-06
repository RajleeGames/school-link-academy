from django.urls import path
from . import views

urlpatterns = [
    path("", views.discipline_home, name="discipline_home"),

    path("categories/", views.discipline_category_list, name="discipline_category_list"),
    path("categories/<int:pk>/edit/", views.discipline_category_update, name="discipline_category_update"),
    path("categories/<int:pk>/delete/", views.discipline_category_delete, name="discipline_category_delete"),

    path("records/", views.discipline_record_list, name="discipline_record_list"),
    path("records/create/", views.discipline_record_create, name="discipline_record_create"),
    path("records/<int:pk>/", views.discipline_record_detail, name="discipline_record_detail"),
    path("records/<int:pk>/edit/", views.discipline_record_update, name="discipline_record_update"),
    path("records/<int:pk>/delete/", views.discipline_record_delete, name="discipline_record_delete"),

    path("followups/", views.followup_list, name="followup_list"),
    path("followups/create/", views.followup_create, name="followup_create"),
    path("followups/<int:pk>/edit/", views.followup_update, name="followup_update"),
    path("followups/<int:pk>/delete/", views.followup_delete, name="followup_delete"),
]