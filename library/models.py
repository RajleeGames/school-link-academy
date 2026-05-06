from django.db import models
from django.utils import timezone

from students.models import Student


class BookCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Book Categories"

    def __str__(self):
        return self.name


class Book(models.Model):
    STATUS_CHOICES = [
        ("available", "Available"),
        ("unavailable", "Unavailable"),
        ("lost", "Lost"),
        ("damaged", "Damaged"),
    ]

    title = models.CharField(max_length=200)

    category = models.ForeignKey(
        BookCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="books"
    )

    author = models.CharField(max_length=150, blank=True)
    publisher = models.CharField(max_length=150, blank=True)
    isbn = models.CharField(max_length=80, blank=True)

    book_code = models.CharField(max_length=80, unique=True)
    shelf_location = models.CharField(max_length=100, blank=True)

    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="available"
    )

    description = models.TextField(blank=True)

    cover_image = models.ImageField(
        upload_to="library/books/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.book_code})"

    @property
    def is_available(self):
        return self.status == "available" and self.available_copies > 0


class BorrowRecord(models.Model):
    STATUS_CHOICES = [
        ("borrowed", "Borrowed"),
        ("returned", "Returned"),
        ("overdue", "Overdue"),
        ("lost", "Lost"),
        ("damaged", "Damaged"),
    ]

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrow_records"
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="library_borrow_records"
    )

    borrowed_date = models.DateField(default=timezone.localdate)
    due_date = models.DateField()
    returned_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="borrowed"
    )

    fine_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-borrowed_date", "-id"]

    def __str__(self):
        return f"{self.book.title} - {self.get_borrower_name()}"

    def get_borrower_name(self):
        if self.student:
            return self.student.full_name
        return "Unknown Student"

    @property
    def is_overdue(self):
        if self.status == "returned":
            return False
        return self.due_date < timezone.localdate()