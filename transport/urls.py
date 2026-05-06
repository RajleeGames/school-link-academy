from django.urls import path

from . import views


urlpatterns = [
    path("", views.transport_home, name="transport_home"),

    path("vehicles/", views.vehicle_list, name="vehicle_list"),
    path("vehicles/create/", views.vehicle_create, name="vehicle_create"),
    path("vehicles/<int:pk>/edit/", views.vehicle_update, name="vehicle_update"),
    path("vehicles/<int:pk>/delete/", views.vehicle_delete, name="vehicle_delete"),

    path("drivers/", views.driver_list, name="driver_list"),
    path("drivers/create/", views.driver_create, name="driver_create"),
    path("drivers/<int:pk>/edit/", views.driver_update, name="driver_update"),
    path("drivers/<int:pk>/delete/", views.driver_delete, name="driver_delete"),

    path("routes/", views.route_list, name="transport_route_list"),
    path("routes/create/", views.route_create, name="transport_route_create"),
    path("routes/<int:pk>/edit/", views.route_update, name="transport_route_update"),
    path("routes/<int:pk>/delete/", views.route_delete, name="transport_route_delete"),

    path("assignments/", views.assignment_list, name="transport_assignment_list"),
    path("assignments/create/", views.assignment_create, name="transport_assignment_create"),
    path("assignments/<int:pk>/edit/", views.assignment_update, name="transport_assignment_update"),
    path("assignments/<int:pk>/delete/", views.assignment_delete, name="transport_assignment_delete"),

    path("trips/", views.trip_log_list, name="trip_log_list"),
    path("trips/create/", views.trip_log_create, name="trip_log_create"),
    path("trips/<int:pk>/edit/", views.trip_log_update, name="trip_log_update"),
    path("trips/<int:pk>/delete/", views.trip_log_delete, name="trip_log_delete"),
]