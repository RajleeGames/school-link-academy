from django.db import models
from students.models import Student
from staff.models import StaffProfile


class StudentAttendance(models.Model):
    STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
        ("sick", "Sick"),
        ("permission", "Permission"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="present")
    arrival_time = models.TimeField(null=True, blank=True)
    remarks = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "student__class_level__order", "student__first_name"]
        unique_together = ["student", "date"]

    def __str__(self):
        return f"{self.student.full_name} - {self.date} - {self.get_status_display()}"


class StaffAttendance(models.Model):
    STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
        ("permission", "Permission"),
        ("sick", "Sick"),
    ]

    staff = models.ForeignKey(
        StaffProfile,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="present")
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    remarks = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "staff__first_name"]
        unique_together = ["staff", "date"]

    def __str__(self):
        return f"{self.staff.full_name} - {self.date} - {self.get_status_display()}"