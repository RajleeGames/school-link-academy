from django.db import models
from django.contrib.auth.models import User

from academics.models import ClassLevel, Subject


class StaffProfile(models.Model):
    ROLE_CHOICES = [
        ("head_teacher", "Head Teacher"),
        ("academic_master", "Academic Master"),
        ("teacher", "Teacher"),

        ("secretary", "Secretary / Receptionist"),
        ("cashier", "Cashier"),
        ("accountant", "Accountant / Bursar"),

        ("librarian", "Librarian"),
        ("hostel_manager", "Hostel Manager"),
        ("transport_manager", "Transport Manager"),
        ("stock_keeper", "Stock Keeper"),

        ("admin_staff", "Admin Staff"),
        ("support_staff", "Support Staff"),
    ]

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("resigned", "Resigned"),
        ("suspended", "Suspended"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staff_profile"
    )

    staff_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=80)
    middle_name = models.CharField(max_length=80, blank=True)
    last_name = models.CharField(max_length=80)

    role = models.CharField(
        max_length=40,
        choices=ROLE_CHOICES,
        default="teacher"
    )

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)

    phone = models.CharField(max_length=30)
    alternative_phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    qualification = models.CharField(max_length=180, blank=True)
    employment_date = models.DateField(null=True, blank=True)

    assigned_classes = models.ManyToManyField(
        ClassLevel,
        related_name="staff_members",
        blank=True
    )

    subjects = models.ManyToManyField(
        Subject,
        related_name="teachers",
        blank=True
    )

    salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    photo = models.ImageField(
        upload_to="staff/photos/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.staff_id} - {self.full_name}"

    @property
    def full_name(self):
        names = [self.first_name, self.middle_name, self.last_name]
        return " ".join([name for name in names if name]).strip()