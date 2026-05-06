from django.urls import path
from . import views

urlpatterns = [
    path("", views.timetable_home, name="timetable_home"),

    path("rooms/", views.room_list, name="room_list"),
    path("rooms/<int:pk>/edit/", views.room_update, name="room_update"),
    path("rooms/<int:pk>/delete/", views.room_delete, name="room_delete"),

    path("slots/", views.time_slot_list, name="time_slot_list"),
    path("slots/auto-create/", views.auto_create_default_time_slots, name="auto_create_default_time_slots"),
    path("slots/<int:pk>/edit/", views.time_slot_update, name="time_slot_update"),
    path("slots/<int:pk>/delete/", views.time_slot_delete, name="time_slot_delete"),

    path("entries/", views.timetable_entry_list, name="timetable_entry_list"),
    path("entries/create/", views.timetable_entry_create, name="timetable_entry_create"),
    path("entries/<int:pk>/edit/", views.timetable_entry_update, name="timetable_entry_update"),
    path("entries/<int:pk>/delete/", views.timetable_entry_delete, name="timetable_entry_delete"),

    path("class/", views.class_timetable, name="class_timetable"),
    path("teacher/", views.teacher_timetable, name="teacher_timetable"),
]