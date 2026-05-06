from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("admin", "Administrator"),
        ("head_teacher", "Head Teacher"),
        ("academic_master", "Academic Master"),
        ("secretary", "Secretary / Receptionist"),
        ("cashier", "Cashier"),
        ("accountant", "Accountant / Bursar"),
        ("teacher", "Teacher"),
        ("librarian", "Librarian"),
        ("hostel_manager", "Hostel Manager"),
        ("transport_manager", "Transport Manager"),
        ("stock_keeper", "Stock Keeper"),
        ("parent", "Parent / Guardian"),
        ("support_staff", "Support Staff"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="account_profile"
    )

    role = models.CharField(
        max_length=40,
        choices=ROLE_CHOICES,
        default="support_staff"
    )

    phone = models.CharField(max_length=30, blank=True)
    must_change_password = models.BooleanField(default=False)
    is_active_profile = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__username"]

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    @property
    def is_admin_role(self):
        return self.role == "admin"

    @property
    def is_parent_role(self):
        return self.role == "parent"

    @property
    def is_teacher_role(self):
        return self.role == "teacher"

    @property
    def is_finance_role(self):
        return self.role in ["cashier", "accountant"]

    @property
    def is_operations_role(self):
        return self.role in [
            "librarian",
            "hostel_manager",
            "transport_manager",
            "stock_keeper",
        ]