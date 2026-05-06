from django.contrib.auth.models import User
from django.db import models

from academics.models import ClassLevel, Stream


class ParentGuardian(models.Model):
    RELATIONSHIP_CHOICES = [
        ("father", "Father"),
        ("mother", "Mother"),
        ("guardian", "Guardian"),
        ("other", "Other"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="parent_guardian_profile"
    )

    full_name = models.CharField(max_length=180)
    relationship = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        default="guardian"
    )
    phone = models.CharField(max_length=30)
    alternative_phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    occupation = models.CharField(max_length=120, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} - {self.phone}"


class Student(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("graduated", "Graduated"),
        ("transferred", "Transferred"),
        ("suspended", "Suspended"),
    ]

    BOARDING_CHOICES = [
        ("day", "Day Student"),
        ("boarding", "Boarding Student"),
    ]

    admission_number = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=80)
    middle_name = models.CharField(max_length=80, blank=True)
    last_name = models.CharField(max_length=80)

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)

    class_level = models.ForeignKey(
        ClassLevel,
        on_delete=models.PROTECT,
        related_name="students"
    )

    stream = models.ForeignKey(
        Stream,
        on_delete=models.PROTECT,
        related_name="students",
        null=True,
        blank=True
    )

    parent_guardian = models.ForeignKey(
        ParentGuardian,
        on_delete=models.PROTECT,
        related_name="students"
    )

    boarding_status = models.CharField(
        max_length=20,
        choices=BOARDING_CHOICES,
        default="day"
    )

    previous_school = models.CharField(max_length=180, blank=True)
    medical_notes = models.TextField(blank=True)
    address = models.TextField(blank=True)

    photo = models.ImageField(
        upload_to="students/photos/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    admission_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["class_level__order", "stream__name", "first_name"]

    def __str__(self):
        return f"{self.admission_number} - {self.full_name}"

    @property
    def full_name(self):
        names = [self.first_name, self.middle_name, self.last_name]
        return " ".join([name for name in names if name]).strip()