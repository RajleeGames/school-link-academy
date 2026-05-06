from django.db import models
from django.utils import timezone

from students.models import Student


class Vehicle(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("maintenance", "Maintenance"),
        ("inactive", "Inactive"),
    ]

    vehicle_name = models.CharField(max_length=120)
    plate_number = models.CharField(max_length=50, unique=True)
    vehicle_type = models.CharField(max_length=80, blank=True)
    capacity = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["vehicle_name"]

    def __str__(self):
        return f"{self.vehicle_name} - {self.plate_number}"


class Driver(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    license_number = models.CharField(max_length=80, blank=True)
    address = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


class TransportRoute(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    name = models.CharField(max_length=120, unique=True)
    pickup_area = models.CharField(max_length=150)
    dropoff_area = models.CharField(max_length=150, blank=True)
    monthly_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="routes"
    )

    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="routes"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class StudentTransportAssignment(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("stopped", "Stopped"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="transport_assignments"
    )

    route = models.ForeignKey(
        TransportRoute,
        on_delete=models.CASCADE,
        related_name="student_assignments"
    )

    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField(null=True, blank=True)

    pickup_point = models.CharField(max_length=150, blank=True)
    guardian_phone = models.CharField(max_length=30, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date", "-id"]

    def __str__(self):
        return f"{self.student.full_name} - {self.route.name}"


class TripLog(models.Model):
    TRIP_TYPE_CHOICES = [
        ("morning_pickup", "Morning Pickup"),
        ("evening_dropoff", "Evening Dropoff"),
        ("other", "Other"),
    ]

    route = models.ForeignKey(
        TransportRoute,
        on_delete=models.CASCADE,
        related_name="trip_logs"
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trip_logs"
    )

    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trip_logs"
    )

    trip_date = models.DateField(default=timezone.localdate)
    trip_type = models.CharField(max_length=30, choices=TRIP_TYPE_CHOICES)
    students_count = models.PositiveIntegerField(default=0)
    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-trip_date", "-id"]

    def __str__(self):
        return f"{self.route.name} - {self.get_trip_type_display()} - {self.trip_date}"