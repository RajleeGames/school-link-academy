from django.contrib import admin

from .models import Hostel, HostelRoom, HostelBed, BoardingAllocation


class HostelRoomInline(admin.TabularInline):
    model = HostelRoom
    extra = 1


class HostelBedInline(admin.TabularInline):
    model = HostelBed
    extra = 1


@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "location")
    inlines = [HostelRoomInline]


@admin.register(HostelRoom)
class HostelRoomAdmin(admin.ModelAdmin):
    list_display = ("room_number", "hostel", "room_type", "capacity", "is_active")
    list_filter = ("hostel", "room_type", "is_active")
    search_fields = ("room_number", "hostel__name")
    inlines = [HostelBedInline]


@admin.register(HostelBed)
class HostelBedAdmin(admin.ModelAdmin):
    list_display = ("bed_number", "room", "status")
    list_filter = ("status", "room__hostel", "room")
    search_fields = ("bed_number", "room__room_number", "room__hostel__name")


@admin.register(BoardingAllocation)
class BoardingAllocationAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "bed",
        "check_in_date",
        "check_out_date",
        "status",
    )
    list_filter = ("status", "check_in_date", "bed__room__hostel")
    search_fields = (
        "student__first_name",
        "student__middle_name",
        "student__last_name",
        "student__admission_number",
        "bed__bed_number",
        "bed__room__room_number",
    )
    list_select_related = ("student", "bed", "bed__room", "bed__room__hostel")