from django.db import models
from django.utils import timezone

from academics.models import AcademicYear, Term, ClassLevel, Stream, Subject
from staff.models import StaffProfile
from students.models import Student


class Homework(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("closed", "Closed"),
        ("cancelled", "Cancelled"),
    ]

    title = models.CharField(max_length=180)
    description = models.TextField()

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="homeworks"
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.PROTECT,
        related_name="homeworks",
        null=True,
        blank=True
    )
    class_level = models.ForeignKey(
        ClassLevel,
        on_delete=models.PROTECT,
        related_name="homeworks"
    )
    stream = models.ForeignKey(
        Stream,
        on_delete=models.SET_NULL,
        related_name="homeworks",
        null=True,
        blank=True
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="homeworks"
    )
    teacher = models.ForeignKey(
        StaffProfile,
        on_delete=models.SET_NULL,
        related_name="homeworks",
        null=True,
        blank=True
    )

    assigned_date = models.DateField(default=timezone.now)
    due_date = models.DateField()

    attachment = models.FileField(
        upload_to="homework/attachments/",
        null=True,
        blank=True
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="published")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-assigned_date", "-id"]

    def __str__(self):
        return f"{self.title} - {self.class_level.name}"


class HomeworkSubmission(models.Model):
    STATUS_CHOICES = [
        ("not_submitted", "Not Submitted"),
        ("submitted", "Submitted"),
        ("late", "Late"),
        ("checked", "Checked"),
        ("returned", "Returned"),
    ]

    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name="submissions"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="homework_submissions"
    )

    submitted_date = models.DateField(null=True, blank=True)
    submitted_file = models.FileField(
        upload_to="homework/submissions/",
        null=True,
        blank=True
    )
    marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    teacher_comment = models.TextField(blank=True)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="not_submitted")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["student__first_name", "student__last_name"]
        unique_together = ["homework", "student"]

    def __str__(self):
        return f"{self.homework.title} - {self.student.full_name}"