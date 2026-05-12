from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Book, BookCategory, BorrowRecord


class BookCategoryForm(forms.ModelForm):
    class Meta:
        model = BookCategory
        fields = [
            "name",
            "description",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Science, Mathematics, Story Books",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Optional description",
            }),
        }


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            "title",
            "category",
            "author",
            "publisher",
            "isbn",
            "book_code",
            "shelf_location",
            "total_copies",
            "available_copies",
            "status",
            "description",
            "cover_image",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Book title",
            }),

            # Searchable if categories become many.
            "category": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search book category...",
            }),

            "author": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Author name",
            }),
            "publisher": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Publisher",
            }),
            "isbn": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "ISBN number",
            }),
            "book_code": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: LIB-001",
            }),
            "shelf_location": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Shelf A2",
            }),
            "total_copies": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
            }),
            "available_copies": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
            }),
            "status": forms.Select(attrs={
                "class": "form-select",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),
            "cover_image": forms.ClearableFileInput(attrs={
                "class": "form-control",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "category" in self.fields:
            self.fields["category"].empty_label = "Search / select category"

    def clean(self):
        cleaned_data = super().clean()

        total_copies = cleaned_data.get("total_copies")
        available_copies = cleaned_data.get("available_copies")

        if total_copies is not None and available_copies is not None:
            if available_copies > total_copies:
                raise ValidationError(
                    "Available copies cannot be greater than total copies."
                )

        return cleaned_data


class BorrowRecordForm(forms.ModelForm):
    class Meta:
        model = BorrowRecord
        fields = [
            "book",
            "student",
            "borrowed_date",
            "due_date",
            "notes",
        ]

        widgets = {
            # Searchable because books can become many.
            "book": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search book by title, code, or ISBN...",
            }),

            # Searchable because students can become many.
            "student": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search student by name or admission number...",
            }),

            "borrowed_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "due_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "book" in self.fields:
            self.fields["book"].empty_label = "Search / select book"

        if "student" in self.fields:
            self.fields["student"].empty_label = "Search / select student"

    def clean(self):
        cleaned_data = super().clean()

        book = cleaned_data.get("book")
        student = cleaned_data.get("student")
        borrowed_date = cleaned_data.get("borrowed_date")
        due_date = cleaned_data.get("due_date")

        if book and not book.is_available:
            raise ValidationError("This book is not available for borrowing.")

        if not student:
            raise ValidationError("Please select a student.")

        if borrowed_date and due_date and due_date < borrowed_date:
            raise ValidationError("Due date cannot be before borrowed date.")

        return cleaned_data


class BorrowReturnForm(forms.ModelForm):
    class Meta:
        model = BorrowRecord
        fields = [
            "returned_date",
            "status",
            "fine_amount",
            "notes",
        ]

        widgets = {
            "returned_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "status": forms.Select(attrs={
                "class": "form-select",
            }),
            "fine_amount": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0,
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),
        }

    def clean(self):
        cleaned_data = super().clean()

        returned_date = cleaned_data.get("returned_date")
        status = cleaned_data.get("status")

        if status == "returned" and not returned_date:
            cleaned_data["returned_date"] = timezone.localdate()

        return cleaned_data