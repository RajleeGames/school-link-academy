from django.db import models
from django.utils import timezone

from students.models import Student


class Hostel(models.Model):
    name = models.CharField(max_length=120, unique=True)
    location = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class HostelRoom(models.Model):
    ROOM_TYPE_CHOICES = [
        ("boys", "Boys"),
        ("girls", "Girls"),
        ("mixed", "Mixed"),
    ]

    hostel = models.ForeignKey(
        Hostel,
        on_delete=models.CASCADE,
        related_name="rooms"
    )
    room_number = models.CharField(max_length=50)
    room_type = models.CharField(
        max_length=20,
        choices=ROOM_TYPE_CHOICES,
        default="boys"
    )
    capacity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["hostel__name", "room_number"]
        unique_together = ["hostel", "room_number"]

    def __str__(self):
        return f"{self.hostel.name} - Room {self.room_number}"

    @property
    def occupied_beds_count(self):
        return self.beds.filter(status="occupied").count()

    @property
    def available_beds_count(self):
        return self.beds.filter(status="available").count()


class HostelBed(models.Model):
    STATUS_CHOICES = [
        ("available", "Available"),
        ("occupied", "Occupied"),
        ("reserved", "Reserved"),
        ("damaged", "Damaged"),
    ]

    room = models.ForeignKey(
        HostelRoom,
        on_delete=models.CASCADE,
        related_name="beds"
    )
    bed_number = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="available"
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["room__hostel__name", "room__room_number", "bed_number"]
        unique_together = ["room", "bed_number"]

    def __str__(self):
        return f"{self.room} - Bed {self.bed_number}"


class BoardingAllocation(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("checked_out", "Checked Out"),
        ("cancelled", "Cancelled"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="boarding_allocations"
    )
    bed = models.ForeignKey(
        HostelBed,
        on_delete=models.CASCADE,
        related_name="allocations"
    )

    check_in_date = models.DateField(default=timezone.localdate)
    check_out_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    guardian_contact = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-check_in_date", "-id"]

    def __str__(self):
        return f"{self.student.full_name} - {self.bed}"

    @property
    def hostel(self):
        return self.bed.room.hostel

    @property
    def room(self):
        return self.bed.room