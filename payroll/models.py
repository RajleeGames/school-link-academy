from django.db import models
from django.utils import timezone

from staff.models import StaffProfile


class SalaryStructure(models.Model):
    staff = models.OneToOneField(
        StaffProfile,
        on_delete=models.CASCADE,
        related_name="salary_structure"
    )

    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    transport_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    housing_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    tax_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    loan_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["staff__first_name", "staff__last_name"]

    def __str__(self):
        return f"{self.staff.full_name} Salary Structure"

    @property
    def total_allowances(self):
        return (
            self.transport_allowance
            + self.housing_allowance
            + self.medical_allowance
            + self.other_allowance
        )

    @property
    def total_deductions(self):
        return (
            self.tax_deduction
            + self.loan_deduction
            + self.other_deduction
        )

    @property
    def net_salary(self):
        return self.basic_salary + self.total_allowances - self.total_deductions


class PayrollRecord(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("approved", "Approved"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]

    MONTH_CHOICES = [
        (1, "January"),
        (2, "February"),
        (3, "March"),
        (4, "April"),
        (5, "May"),
        (6, "June"),
        (7, "July"),
        (8, "August"),
        (9, "September"),
        (10, "October"),
        (11, "November"),
        (12, "December"),
    ]

    staff = models.ForeignKey(
        StaffProfile,
        on_delete=models.CASCADE,
        related_name="payroll_records"
    )

    month = models.PositiveSmallIntegerField(choices=MONTH_CHOICES)
    year = models.PositiveIntegerField(default=timezone.localdate().year)

    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=80, blank=True)
    reference = models.CharField(max_length=120, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "-month", "staff__first_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["staff", "month", "year"],
                name="unique_staff_payroll_per_month"
            )
        ]

    def __str__(self):
        return f"{self.staff.full_name} - {self.get_month_display()} {self.year}"

    @property
    def calculated_net_salary(self):
        return self.basic_salary + self.total_allowances - self.total_deductions

    def save(self, *args, **kwargs):
        self.net_salary = self.calculated_net_salary
        super().save(*args, **kwargs)