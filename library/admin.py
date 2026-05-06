from django.contrib import admin

from .models import Book, BookCategory, BorrowRecord


@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "book_code",
        "category",
        "author",
        "total_copies",
        "available_copies",
        "status",
    )
    list_filter = ("category", "status")
    search_fields = ("title", "book_code", "author", "isbn")
    list_select_related = ("category",)


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = (
        "book",
        "student",
        "borrowed_date",
        "due_date",
        "returned_date",
        "status",
        "fine_amount",
    )
    list_filter = ("status", "borrowed_date", "due_date")
    search_fields = (
        "book__title",
        "book__book_code",
        "student__first_name",
        "student__middle_name",
        "student__last_name",
        "student__admission_number",
    )
    list_select_related = ("book", "student")