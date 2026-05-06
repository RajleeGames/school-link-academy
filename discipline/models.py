from django.db import models
from django.utils import timezone

from students.models import Student
from staff.models import StaffProfile


class DisciplineCategory(models.Model):
    CATEGORY_TYPE_CHOICES = [
        ("incident", "Incident"),
        ("reward", "Reward"),
        ("warning", "Warning"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=120, unique=True)
    category_type = models.CharField(
        max_length=20,
        choices=CATEGORY_TYPE_CHOICES,
        default="incident"
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["category_type", "name"]
        verbose_name_plural = "Discipline Categories"

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class DisciplineRecord(models.Model):
    RECORD_TYPE_CHOICES = [
        ("incident", "Incident"),
        ("warning", "Warning"),
        ("reward", "Reward"),
        ("follow_up", "Follow Up"),
    ]

    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    STATUS_CHOICES = [
        ("open", "Open"),
        ("under_review", "Under Review"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="discipline_records"
    )
    record_type = models.CharField(
        max_length=20,
        choices=RECORD_TYPE_CHOICES,
        default="incident"
    )
    category = models.ForeignKey(
        DisciplineCategory,
        on_delete=models.SET_NULL,
        related_name="records",
        null=True,
        blank=True
    )

    title = models.CharField(max_length=180)
    description = models.TextField()

    incident_date = models.DateField(default=timezone.now)
    incident_time = models.TimeField(null=True, blank=True)

    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default="low"
    )
    action_taken = models.TextField(blank=True)

    reported_by = models.ForeignKey(
        StaffProfile,
        on_delete=models.SET_NULL,
        related_name="reported_discipline_records",
        null=True,
        blank=True
    )

    parent_notified = models.BooleanField(default=False)
    parent_feedback = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open"
    )
    attachment = models.FileField(
        upload_to="discipline/attachments/",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-incident_date", "-id"]

    def __str__(self):
        return f"{self.student.full_name} - {self.title}"


class DisciplineFollowUp(models.Model):
    record = models.ForeignKey(
        DisciplineRecord,
        on_delete=models.CASCADE,
        related_name="followups"
    )
    follow_up_date = models.DateField(default=timezone.now)
    note = models.TextField()
    handled_by = models.ForeignKey(
        StaffProfile,
        on_delete=models.SET_NULL,
        related_name="discipline_followups",
        null=True,
        blank=True
    )
    next_action = models.CharField(max_length=180, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-follow_up_date", "-id"]

    def __str__(self):
        return f"{self.record.title} - {self.follow_up_date}"