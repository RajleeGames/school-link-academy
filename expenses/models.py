from django.db import models
from django.utils import timezone


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Expense Categories"

    def __str__(self):
        return self.name


class Expense(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Cash"),
        ("bank", "Bank"),
        ("mobile_money", "Mobile Money"),
        ("card", "Card"),
        ("cheque", "Cheque"),
    ]

    STATUS_CHOICES = [
        ("paid", "Paid"),
        ("pending", "Pending"),
        ("cancelled", "Cancelled"),
    ]

    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name="expenses"
    )
    expense_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    expense_date = models.DateField(default=timezone.now)

    payment_method = models.CharField(
        max_length=30,
        choices=PAYMENT_METHOD_CHOICES,
        default="cash"
    )
    reference = models.CharField(max_length=120, blank=True)

    paid_to = models.CharField(max_length=180, blank=True)
    recorded_by = models.CharField(max_length=120, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="paid"
    )

    receipt_file = models.FileField(
        upload_to="expenses/receipts/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-expense_date", "-id"]

    def __str__(self):
        return f"{self.expense_number} - {self.title}"