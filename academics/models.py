from django.db import models


class AcademicYear(models.Model):
    name = models.CharField(max_length=50, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.name


class Term(models.Model):
    TERM_CHOICES = [
        ("term_1", "Term 1"),
        ("term_2", "Term 2"),
        ("term_3", "Term 3"),
        ("semester_1", "Semester 1"),
        ("semester_2", "Semester 2"),
    ]

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="terms"
    )
    name = models.CharField(max_length=30, choices=TERM_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_date"]
        unique_together = ["academic_year", "name"]

    def __str__(self):
        return f"{self.get_name_display()} - {self.academic_year.name}"


class ClassLevel(models.Model):
    LEVEL_CHOICES = [
        ("primary", "Primary"),
        ("secondary", "Secondary"),
        ("advanced", "Advanced Secondary"),
    ]

    name = models.CharField(max_length=80)
    level_type = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default="primary"
    )
    order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Stream(models.Model):
    class_level = models.ForeignKey(
        ClassLevel,
        on_delete=models.CASCADE,
        related_name="streams"
    )
    name = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["class_level__order", "name"]
        unique_together = ["class_level", "name"]

    def __str__(self):
        return f"{self.class_level.name} {self.name}"


class Subject(models.Model):
    SUBJECT_TYPE_CHOICES = [
        ("compulsory", "Compulsory"),
        ("optional", "Optional"),
    ]

    name = models.CharField(max_length=120)
    code = models.CharField(max_length=30, unique=True)
    subject_type = models.CharField(
        max_length=20,
        choices=SUBJECT_TYPE_CHOICES,
        default="compulsory"
    )
    class_levels = models.ManyToManyField(
        ClassLevel,
        related_name="subjects",
        blank=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name