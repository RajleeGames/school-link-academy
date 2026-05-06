from django.contrib import admin
from .models import Room, TimeSlot, TimetableEntry


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ("name", "start_time", "end_time", "is_break", "is_active")
    search_fields = ("name",)
    list_filter = ("is_break", "is_active")


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = (
        "class_level",
        "stream",
        "day",
        "time_slot",
        "subject",
        "teacher",
        "room",
        "is_active",
    )
    list_filter = ("class_level", "stream", "day", "subject", "teacher", "is_active")
    search_fields = (
        "class_level__name",
        "stream__name",
        "subject__name",
        "teacher__first_name",
        "teacher__last_name",
        "room__name",
    )