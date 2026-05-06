from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import permission_required

from .forms import BookCategoryForm, BookForm, BorrowRecordForm, BorrowReturnForm
from .models import Book, BookCategory, BorrowRecord


def safe_delete_object(request, obj, success_message, redirect_url):
    try:
        obj.delete()
        messages.success(request, success_message)
    except ProtectedError:
        messages.error(
            request,
            "This record cannot be deleted because it is already used somewhere. You can edit it instead."
        )
    except Exception:
        messages.error(
            request,
            "This record could not be deleted. Please check if it is connected to other records."
        )

    return redirect(redirect_url)


def restore_book_copy_if_needed(record):
    """
    If a borrow record is deleted while still borrowed/overdue,
    return the copy back to the book stock.
    """
    if record.status in ["borrowed", "overdue"]:
        book = record.book

        if book.available_copies < book.total_copies:
            book.available_copies += 1

        if book.available_copies > 0 and book.status == "unavailable":
            book.status = "available"

        book.save()


@permission_required("library.view")
def library_home(request):
    today = timezone.localdate()

    total_books = Book.objects.count()
    total_copies = Book.objects.aggregate(total=Sum("total_copies"))["total"] or 0
    available_copies = Book.objects.aggregate(total=Sum("available_copies"))["total"] or 0

    borrowed_count = BorrowRecord.objects.filter(status="borrowed").count()

    overdue_count = BorrowRecord.objects.filter(
        status="borrowed",
        due_date__lt=today
    ).count()

    recent_borrows = BorrowRecord.objects.select_related(
        "book",
        "student",
    ).order_by("-id")[:8]

    categories = BookCategory.objects.annotate(
        book_count=Count("books")
    ).order_by("name")[:8]

    context = {
        "total_books": total_books,
        "total_copies": total_copies,
        "available_copies": available_copies,
        "borrowed_count": borrowed_count,
        "overdue_count": overdue_count,
        "recent_borrows": recent_borrows,
        "categories": categories,
    }

    return render(request, "library/home.html", context)


@permission_required("library.view")
def book_list(request):
    books = Book.objects.select_related("category")

    search = request.GET.get("search", "").strip()
    category_id = request.GET.get("category", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        books = books.filter(
            Q(title__icontains=search)
            | Q(book_code__icontains=search)
            | Q(author__icontains=search)
            | Q(isbn__icontains=search)
        )

    if category_id:
        books = books.filter(category_id=category_id)

    if status:
        books = books.filter(status=status)

    context = {
        "books": books,
        "categories": BookCategory.objects.all(),
        "search": search,
        "selected_category": category_id,
        "selected_status": status,
    }

    return render(request, "library/book_list.html", context)


@permission_required("library.manage")
def book_create(request):
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "Book added successfully.")
            return redirect("book_list")

        messages.error(request, "Please correct the book form.")
    else:
        form = BookForm()

    return render(request, "library/book_form.html", {
        "form": form,
        "title": "Add Book",
        "button_text": "Save Book",
        "is_category_form": False,
        "is_update": False,
    })


@permission_required("library.manage")
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        form = BookForm(request.POST, request.FILES, instance=book)

        if form.is_valid():
            form.save()
            messages.success(request, "Book updated successfully.")
            return redirect("book_list")

        messages.error(request, "Please correct the book form.")
    else:
        form = BookForm(instance=book)

    return render(request, "library/book_form.html", {
        "form": form,
        "book": book,
        "title": "Edit Book",
        "button_text": "Update Book",
        "is_category_form": False,
        "is_update": True,
    })


@permission_required("library.manage")
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if BorrowRecord.objects.filter(book=book).exists():
        messages.error(
            request,
            "This book has borrow records. Do not delete it. Change status to unavailable, lost, or damaged instead."
        )
        return redirect("book_list")

    if request.method == "POST":
        return safe_delete_object(
            request,
            book,
            "Book deleted successfully.",
            "book_list"
        )

    return redirect("book_list")


@permission_required("library.view")
def category_list(request):
    categories = BookCategory.objects.annotate(
        book_count=Count("books")
    ).order_by("name")

    return render(request, "library/category_list.html", {
        "categories": categories,
    })


@permission_required("library.manage")
def category_create(request):
    if request.method == "POST":
        form = BookCategoryForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Book category added successfully.")
            return redirect("book_category_list")

        messages.error(request, "Please correct the category form.")
    else:
        form = BookCategoryForm()

    return render(request, "library/book_form.html", {
        "form": form,
        "title": "Add Book Category",
        "button_text": "Save Category",
        "is_category_form": True,
        "is_update": False,
    })


@permission_required("library.manage")
def category_update(request, pk):
    category = get_object_or_404(BookCategory, pk=pk)

    if request.method == "POST":
        form = BookCategoryForm(request.POST, instance=category)

        if form.is_valid():
            form.save()
            messages.success(request, "Book category updated successfully.")
            return redirect("book_category_list")

        messages.error(request, "Please correct the category form.")
    else:
        form = BookCategoryForm(instance=category)

    return render(request, "library/book_form.html", {
        "form": form,
        "category": category,
        "title": "Edit Book Category",
        "button_text": "Update Category",
        "is_category_form": True,
        "is_update": True,
    })


@permission_required("library.manage")
def category_delete(request, pk):
    category = get_object_or_404(BookCategory, pk=pk)

    if Book.objects.filter(category=category).exists():
        messages.error(
            request,
            "This category has books. Move those books to another category before deleting it."
        )
        return redirect("book_category_list")

    if request.method == "POST":
        return safe_delete_object(
            request,
            category,
            "Book category deleted successfully.",
            "book_category_list"
        )

    return redirect("book_category_list")


@permission_required("library.view")
def borrow_list(request):
    records = BorrowRecord.objects.select_related(
        "book",
        "student",
    )

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        records = records.filter(
            Q(book__title__icontains=search)
            | Q(book__book_code__icontains=search)
            | Q(student__first_name__icontains=search)
            | Q(student__middle_name__icontains=search)
            | Q(student__last_name__icontains=search)
            | Q(student__admission_number__icontains=search)
        )

    if status:
        records = records.filter(status=status)

    context = {
        "records": records,
        "search": search,
        "selected_status": status,
    }

    return render(request, "library/borrow_list.html", context)


@permission_required("library.manage")
def borrow_create(request):
    if request.method == "POST":
        form = BorrowRecordForm(request.POST)

        if form.is_valid():
            borrow = form.save(commit=False)

            if borrow.book.available_copies <= 0:
                messages.error(request, "This book has no available copies.")
                return render(request, "library/borrow_form.html", {
                    "form": form,
                    "title": "Borrow Book",
                    "button_text": "Save Borrow Record",
                    "is_update": False,
                })

            borrow.status = "borrowed"
            borrow.save()

            book = borrow.book
            book.available_copies -= 1

            if book.available_copies == 0:
                book.status = "unavailable"

            book.save()

            messages.success(request, "Book borrowed successfully.")
            return redirect("borrow_detail", pk=borrow.pk)

        messages.error(request, "Please correct the borrow form.")
    else:
        form = BorrowRecordForm()

    return render(request, "library/borrow_form.html", {
        "form": form,
        "title": "Borrow Book",
        "button_text": "Save Borrow Record",
        "is_update": False,
    })


@permission_required("library.view")
def borrow_detail(request, pk):
    record = get_object_or_404(
        BorrowRecord.objects.select_related(
            "book",
            "student",
        ),
        pk=pk
    )

    return render(request, "library/borrow_detail.html", {
        "record": record,
    })


@permission_required("library.manage")
def borrow_return(request, pk):
    record = get_object_or_404(
        BorrowRecord.objects.select_related("book", "student"),
        pk=pk
    )

    old_status = record.status

    if request.method == "POST":
        form = BorrowReturnForm(request.POST, instance=record)

        if form.is_valid():
            returned_record = form.save(commit=False)

            if returned_record.status == "returned" and not returned_record.returned_date:
                returned_record.returned_date = timezone.localdate()

            returned_record.save()

            if old_status != "returned" and returned_record.status == "returned":
                book = returned_record.book

                if book.available_copies < book.total_copies:
                    book.available_copies += 1

                if book.available_copies > 0 and book.status == "unavailable":
                    book.status = "available"

                book.save()

            if returned_record.status in ["lost", "damaged"]:
                book = returned_record.book

                if book.available_copies > 0:
                    book.status = "available"
                else:
                    book.status = "unavailable"

                book.save()

            messages.success(request, "Book return updated successfully.")
            return redirect("borrow_detail", pk=record.pk)

        messages.error(request, "Please correct the return form.")
    else:
        form = BorrowReturnForm(instance=record)

    return render(request, "library/borrow_form.html", {
        "form": form,
        "record": record,
        "title": "Return / Update Borrow Record",
        "button_text": "Update Record",
        "is_update": True,
    })


@permission_required("library.manage")
def borrow_delete(request, pk):
    record = get_object_or_404(
        BorrowRecord.objects.select_related("book"),
        pk=pk
    )

    if request.method == "POST":
        restore_book_copy_if_needed(record)
        record.delete()
        messages.success(request, "Borrow record deleted successfully.")
        return redirect("borrow_list")

    return redirect("borrow_list")