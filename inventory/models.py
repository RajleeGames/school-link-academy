from django.db import models
from django.utils import timezone


class InventoryCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Inventory Categories"

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    contact_person = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    name = models.CharField(max_length=150)
    item_code = models.CharField(max_length=80, unique=True)

    category = models.ForeignKey(
        InventoryCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="items"
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="items"
    )

    unit = models.CharField(max_length=50, default="pcs")
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)

    buying_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    location = models.CharField(max_length=120, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.item_code})"

    @property
    def is_low_stock(self):
        return self.quantity <= self.reorder_level


class StockIn(models.Model):
    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name="stock_ins"
    )

    quantity = models.PositiveIntegerField()
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_ins"
    )

    buying_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    received_date = models.DateField(default=timezone.localdate)
    reference = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-received_date", "-id"]
        verbose_name_plural = "Stock In"

    def __str__(self):
        return f"{self.item.name} +{self.quantity}"


class StockOut(models.Model):
    PURPOSE_CHOICES = [
        ("issued", "Issued"),
        ("used", "Used"),
        ("damaged", "Damaged"),
        ("lost", "Lost"),
        ("other", "Other"),
    ]

    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name="stock_outs"
    )

    quantity = models.PositiveIntegerField()
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default="issued")
    issued_to = models.CharField(max_length=150, blank=True)
    issued_date = models.DateField(default=timezone.localdate)
    reference = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-issued_date", "-id"]
        verbose_name_plural = "Stock Out"

    def __str__(self):
        return f"{self.item.name} -{self.quantity}"