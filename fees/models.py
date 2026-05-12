from decimal import Decimal

from django.db import models
from django.utils import timezone

from academics.models import AcademicYear, ClassLevel, Term
from students.models import Student


class FeeCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Fee Categories"

    def __str__(self):
        return self.name


class FeeStructure(models.Model):
    category = models.ForeignKey(
        FeeCategory,
        on_delete=models.PROTECT,
        related_name="fee_structures"
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="fee_structures"
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.PROTECT,
        related_name="fee_structures",
        null=True,
        blank=True
    )
    class_level = models.ForeignKey(
        ClassLevel,
        on_delete=models.PROTECT,
        related_name="fee_structures"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_required = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["class_level__order", "category__name"]
        unique_together = ["category", "academic_year", "term", "class_level"]

    def __str__(self):
        return f"{self.class_level.name} - {self.category.name} - {self.amount}"


class StudentInvoice(models.Model):
    STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("partial", "Partial"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="fee_invoices"
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="student_invoices"
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.PROTECT,
        related_name="student_invoices",
        null=True,
        blank=True
    )
    invoice_number = models.CharField(max_length=50, unique=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="unpaid")
    notes = models.TextField(blank=True)

    invoice_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-invoice_date", "-id"]

    def __str__(self):
        return f"{self.invoice_number} - {self.student.full_name}"

    @property
    def payable_amount(self):
        return max(Decimal("0.00"), self.total_amount - self.discount_amount)

    @property
    def paid_amount(self):
        total = self.payments.filter(status="confirmed").aggregate(
            total=models.Sum("amount")
        )["total"]
        return total or Decimal("0.00")

    @property
    def balance(self):
        return max(Decimal("0.00"), self.payable_amount - self.paid_amount)

    def refresh_status(self):
        if self.status == "cancelled":
            return

        if self.paid_amount <= 0:
            self.status = "unpaid"
        elif self.balance > 0:
            self.status = "partial"
        else:
            self.status = "paid"

        self.save(update_fields=["status"])


class StudentInvoiceItem(models.Model):
    invoice = models.ForeignKey(
        StudentInvoice,
        on_delete=models.CASCADE,
        related_name="items"
    )
    category = models.ForeignKey(
        FeeCategory,
        on_delete=models.PROTECT,
        related_name="invoice_items"
    )
    description = models.CharField(max_length=180, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["category__name"]

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.category.name}"


class FeePayment(models.Model):
    METHOD_CHOICES = [
        ("cash", "Cash"),
        ("bank", "Bank"),
        ("mobile_money", "Mobile Money"),
        ("card", "Card"),
        ("cheque", "Cheque"),
    ]

    STATUS_CHOICES = [
        ("confirmed", "Confirmed"),
        ("pending", "Pending"),
        ("cancelled", "Cancelled"),
    ]

    invoice = models.ForeignKey(
        StudentInvoice,
        on_delete=models.PROTECT,
        related_name="payments"
    )

    # NEW: this tells system what the payment is for.
    fee_item = models.ForeignKey(
        StudentInvoiceItem,
        on_delete=models.PROTECT,
        related_name="payments",
        null=True,
        blank=True,
        help_text="Optional. Select the fee item this payment is paying for."
    )

    receipt_number = models.CharField(max_length=50, unique=True)
    payment_date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=30, choices=METHOD_CHOICES, default="cash")
    reference = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="confirmed")
    received_by = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-payment_date", "-id"]

    def __str__(self):
        return f"{self.receipt_number} - {self.amount}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.invoice.refresh_status()