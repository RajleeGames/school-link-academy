from django.db import models

from academics.models import ClassLevel, Stream, Subject
from staff.models import StaffProfile


class Room(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class TimeSlot(models.Model):
    name = models.CharField(max_length=120)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_break = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"


class TimetableEntry(models.Model):
    DAY_CHOICES = [
        ("monday", "Monday"),
        ("tuesday", "Tuesday"),
        ("wednesday", "Wednesday"),
        ("thursday", "Thursday"),
        ("friday", "Friday"),
        ("saturday", "Saturday"),
        ("sunday", "Sunday"),
    ]

    class_level = models.ForeignKey(
        ClassLevel,
        on_delete=models.CASCADE,
        related_name="timetable_entries"
    )
    stream = models.ForeignKey(
        Stream,
        on_delete=models.SET_NULL,
        related_name="timetable_entries",
        null=True,
        blank=True
    )
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    time_slot = models.ForeignKey(
        TimeSlot,
        on_delete=models.PROTECT,
        related_name="timetable_entries"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="timetable_entries",
        null=True,
        blank=True
    )
    teacher = models.ForeignKey(
        StaffProfile,
        on_delete=models.SET_NULL,
        related_name="timetable_entries",
        null=True,
        blank=True
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        related_name="timetable_entries",
        null=True,
        blank=True
    )
    note = models.CharField(max_length=180, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["class_level__order", "stream__name", "day", "time_slot__start_time"]
        unique_together = ["class_level", "stream", "day", "time_slot"]

    def __str__(self):
        stream_name = f" {self.stream.name}" if self.stream else ""
        return f"{self.class_level.name}{stream_name} - {self.get_day_display()} - {self.time_slot.name}"