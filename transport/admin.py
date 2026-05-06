from django.contrib import admin

from .models import Driver, StudentTransportAssignment, TransportRoute, TripLog, Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("vehicle_name", "plate_number", "vehicle_type", "capacity", "status")
    list_filter = ("status", "vehicle_type")
    search_fields = ("vehicle_name", "plate_number")


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "license_number", "status")
    list_filter = ("status",)
    search_fields = ("full_name", "phone", "license_number")


@admin.register(TransportRoute)
class TransportRouteAdmin(admin.ModelAdmin):
    list_display = ("name", "pickup_area", "monthly_fee", "vehicle", "driver", "status")
    list_filter = ("status",)
    search_fields = ("name", "pickup_area", "dropoff_area")
    list_select_related = ("vehicle", "driver")


@admin.register(StudentTransportAssignment)
class StudentTransportAssignmentAdmin(admin.ModelAdmin):
    list_display = ("student", "route", "pickup_point", "start_date", "end_date", "status")
    list_filter = ("status", "route")
    search_fields = (
        "student__first_name",
        "student__middle_name",
        "student__last_name",
        "student__admission_number",
        "route__name",
        "pickup_point",
    )
    list_select_related = ("student", "route")


@admin.register(TripLog)
class TripLogAdmin(admin.ModelAdmin):
    list_display = ("route", "trip_date", "trip_type", "vehicle", "driver", "students_count")
    list_filter = ("trip_type", "trip_date", "route")
    search_fields = ("route__name", "vehicle__plate_number", "driver__full_name")
    list_select_related = ("route", "vehicle", "driver")