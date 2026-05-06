from django.db import models
from django.utils import timezone

from academics.models import AcademicYear, Term, ClassLevel, Subject
from students.models import Student
from staff.models import StaffProfile


class ExamType(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Exam(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("open", "Open"),
        ("closed", "Closed"),
        ("published", "Published"),
    ]

    name = models.CharField(max_length=180)
    exam_type = models.ForeignKey(
        ExamType,
        on_delete=models.PROTECT,
        related_name="exams"
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="exams"
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.PROTECT,
        related_name="exams",
        null=True,
        blank=True
    )
    class_level = models.ForeignKey(
        ClassLevel,
        on_delete=models.PROTECT,
        related_name="exams"
    )
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date", "class_level__order", "name"]

    def __str__(self):
        return f"{self.name} - {self.class_level.name}"


class GradeScale(models.Model):
    grade = models.CharField(max_length=5)
    min_score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    remark = models.CharField(max_length=120, blank=True)
    points = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-min_score"]

    def __str__(self):
        return f"{self.grade}: {self.min_score} - {self.max_score}"


class ExamResult(models.Model):
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="results"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="exam_results"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="exam_results"
    )
    teacher = models.ForeignKey(
        StaffProfile,
        on_delete=models.SET_NULL,
        related_name="marked_results",
        null=True,
        blank=True
    )

    marks = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=5, blank=True)
    points = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    remark = models.CharField(max_length=120, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            "exam__class_level__order",
            "student__first_name",
            "subject__name",
        ]
        unique_together = ["exam", "student", "subject"]

    def __str__(self):
        return f"{self.student.full_name} - {self.subject.name} - {self.marks}"

    def apply_grade(self):
        grade_scale = GradeScale.objects.filter(
            is_active=True,
            min_score__lte=self.marks,
            max_score__gte=self.marks
        ).first()

        if grade_scale:
            self.grade = grade_scale.grade
            self.points = grade_scale.points
            self.remark = grade_scale.remark
        else:
            self.grade = ""
            self.points = 0
            self.remark = ""

    def save(self, *args, **kwargs):
        self.apply_grade()
        super().save(*args, **kwargs)