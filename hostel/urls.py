from django.urls import path

from . import views


urlpatterns = [
    path("", views.hostel_home, name="hostel_home"),

    path("hostels/", views.hostel_list, name="hostel_list"),
    path("hostels/create/", views.hostel_create, name="hostel_create"),
    path("hostels/<int:pk>/edit/", views.hostel_update, name="hostel_update"),
    path("hostels/<int:pk>/delete/", views.hostel_delete, name="hostel_delete"),

    path("rooms/", views.room_list, name="hostel_room_list"),
    path("rooms/create/", views.room_create, name="hostel_room_create"),
    path("rooms/<int:pk>/edit/", views.room_update, name="hostel_room_update"),
    path("rooms/<int:pk>/delete/", views.room_delete, name="hostel_room_delete"),

    path("beds/", views.bed_list, name="hostel_bed_list"),
    path("beds/create/", views.bed_create, name="hostel_bed_create"),
    path("beds/<int:pk>/edit/", views.bed_update, name="hostel_bed_update"),
    path("beds/<int:pk>/delete/", views.bed_delete, name="hostel_bed_delete"),

    path("allocations/", views.allocation_list, name="boarding_allocation_list"),
    path("allocations/create/", views.allocation_create, name="boarding_allocation_create"),
    path("allocations/<int:pk>/", views.allocation_detail, name="boarding_allocation_detail"),
    path("allocations/<int:pk>/checkout/", views.allocation_checkout, name="boarding_allocation_checkout"),
    path("allocations/<int:pk>/delete/", views.allocation_delete, name="boarding_allocation_delete"),
]