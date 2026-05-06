from decimal import Decimal

from django.contrib import messages
from django.db.models import Q, Sum
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import permission_required
from audit.utils import log_audit, model_to_dict_safe

from fees.models import FeePayment

from .forms import ExpenseCategoryForm, ExpenseForm
from .models import ExpenseCategory, Expense


# =====================================================
# HELPERS
# =====================================================

def generate_expense_number():
    last_expense = Expense.objects.order_by("-id").first()
    next_id = 1 if not last_expense else last_expense.id + 1
    return f"EXP-{next_id:05d}"


def expense_category_audit_message(category, prefix):
    return f"{prefix} expense category {category.name}"


def expense_audit_message(expense, prefix):
    return f"{prefix} expense {expense.expense_number} - {expense.title}"


def safe_delete_object(request, obj, success_message, redirect_url, audit_message=None):
    old_values = model_to_dict_safe(obj)
    object_repr = str(obj)

    try:
        log_audit(
            request,
            action="delete",
            obj=obj,
            message=audit_message or f"Deleted {object_repr}",
            old_values=old_values,
            new_values={},
        )

        obj.delete()
        messages.success(request, success_message)

    except ProtectedError:
        messages.error(
            request,
            "This record cannot be deleted because it is already used somewhere. "
            "You can edit it or mark it inactive instead."
        )

    except Exception:
        messages.error(
            request,
            "This record could not be deleted. Please check if it is connected to other records."
        )

    return redirect(redirect_url)


# =====================================================
# EXPENSES HOME
# =====================================================

@permission_required("expenses.view")
def expenses_home(request):
    total_income = FeePayment.objects.filter(status="confirmed").aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    total_expenses = Expense.objects.filter(status="paid").aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    pending_expenses = Expense.objects.filter(status="pending").aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    net_cash = total_income - total_expenses

    recent_expenses = Expense.objects.select_related(
        "category"
    ).order_by("-created_at")[:8]

    recent_payments = FeePayment.objects.select_related(
        "invoice",
        "invoice__student"
    ).order_by("-created_at")[:8]

    context = {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "pending_expenses": pending_expenses,
        "net_cash": net_cash,
        "recent_expenses": recent_expenses,
        "recent_payments": recent_payments,
    }

    return render(request, "expenses/home.html", context)


# =====================================================
# EXPENSE CATEGORIES
# =====================================================

@permission_required("expenses.manage")
def expense_category_list(request):
    categories = ExpenseCategory.objects.all()

    if request.method == "POST":
        form = ExpenseCategoryForm(request.POST)

        if form.is_valid():
            category = form.save()

            log_audit(
                request,
                action="create",
                obj=category,
                message=expense_category_audit_message(category, "Created"),
                old_values={},
                new_values=model_to_dict_safe(category),
            )

            messages.success(request, "Expense category saved successfully.")
            return redirect("expense_category_list")

        messages.error(request, "Please correct the category form.")
    else:
        form = ExpenseCategoryForm()

    return render(request, "expenses/category_list.html", {
        "categories": categories,
        "form": form,
    })


@permission_required("expenses.manage")
def expense_category_update(request, pk):
    category = get_object_or_404(ExpenseCategory, pk=pk)

    if request.method == "POST":
        old_values = model_to_dict_safe(category)
        form = ExpenseCategoryForm(request.POST, instance=category)

        if form.is_valid():
            category = form.save()

            log_audit(
                request,
                action="update",
                obj=category,
                message=expense_category_audit_message(category, "Updated"),
                old_values=old_values,
                new_values=model_to_dict_safe(category),
            )

            messages.success(request, "Expense category updated successfully.")
            return redirect("expense_category_list")

        messages.error(request, "Please correct the category form.")
    else:
        form = ExpenseCategoryForm(instance=category)

    return render(request, "expenses/simple_expense_form.html", {
        "form": form,
        "title": "Update Expense Category",
        "button_text": "Update Category",
        "back_url": "expense_category_list",
    })


@permission_required("expenses.manage")
def expense_category_delete(request, pk):
    category = get_object_or_404(ExpenseCategory, pk=pk)

    if request.method == "POST":
        return safe_delete_object(
            request,
            category,
            "Expense category deleted successfully.",
            "expense_category_list",
            audit_message=expense_category_audit_message(category, "Deleted"),
        )

    return redirect("expense_category_list")


# =====================================================
# EXPENSE RECORDS
# =====================================================

@permission_required("expenses.view")
def expense_list(request):
    query = request.GET.get("q", "").strip()
    category_filter = request.GET.get("category", "").strip()
    status_filter = request.GET.get("status", "").strip()
    method_filter = request.GET.get("method", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()

    expenses = Expense.objects.select_related("category").all()

    if query:
        expenses = expenses.filter(
            Q(expense_number__icontains=query) |
            Q(title__icontains=query) |
            Q(paid_to__icontains=query) |
            Q(reference__icontains=query)
        )

    if category_filter:
        expenses = expenses.filter(category_id=category_filter)

    if status_filter:
        expenses = expenses.filter(status=status_filter)

    if method_filter:
        expenses = expenses.filter(payment_method=method_filter)

    if date_from:
        expenses = expenses.filter(expense_date__gte=date_from)

    if date_to:
        expenses = expenses.filter(expense_date__lte=date_to)

    total_filtered = expenses.filter(status="paid").aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    context = {
        "expenses": expenses,
        "categories": ExpenseCategory.objects.filter(is_active=True),
        "query": query,
        "category_filter": category_filter,
        "status_filter": status_filter,
        "method_filter": method_filter,
        "date_from": date_from,
        "date_to": date_to,
        "total_filtered": total_filtered,
        "status_choices": Expense.STATUS_CHOICES,
        "method_choices": Expense.PAYMENT_METHOD_CHOICES,
    }

    return render(request, "expenses/expense_list.html", context)


@permission_required("expenses.manage")
def expense_create(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST, request.FILES)

        if form.is_valid():
            expense = form.save()

            log_audit(
                request,
                action="create",
                obj=expense,
                message=expense_audit_message(expense, "Created"),
                old_values={},
                new_values=model_to_dict_safe(expense),
            )

            messages.success(request, "Expense recorded successfully.")
            return redirect("expense_detail", pk=expense.pk)

        messages.error(request, "Please correct the expense form.")
    else:
        form = ExpenseForm(initial={
            "expense_number": generate_expense_number(),
            "expense_date": timezone.now().date(),
            "status": "paid",
        })

    return render(request, "expenses/expense_form.html", {
        "form": form,
        "title": "Record Expense",
        "button_text": "Save Expense",
        "is_update": False,
    })


@permission_required("expenses.manage")
def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk)

    if request.method == "POST":
        old_values = model_to_dict_safe(expense)
        form = ExpenseForm(request.POST, request.FILES, instance=expense)

        if form.is_valid():
            updated_expense = form.save()

            log_audit(
                request,
                action="update",
                obj=updated_expense,
                message=expense_audit_message(updated_expense, "Updated"),
                old_values=old_values,
                new_values=model_to_dict_safe(updated_expense),
            )

            messages.success(request, "Expense updated successfully.")
            return redirect("expense_detail", pk=updated_expense.pk)

        messages.error(request, "Please correct the expense form.")
    else:
        form = ExpenseForm(instance=expense)

    return render(request, "expenses/expense_form.html", {
        "form": form,
        "expense": expense,
        "title": "Update Expense",
        "button_text": "Update Expense",
        "is_update": True,
    })


@permission_required("expenses.manage")
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)

    if request.method == "POST":
        return safe_delete_object(
            request,
            expense,
            "Expense deleted successfully.",
            "expense_list",
            audit_message=expense_audit_message(expense, "Deleted"),
        )

    return redirect("expense_list")


@permission_required("expenses.view")
def expense_detail(request, pk):
    expense = get_object_or_404(
        Expense.objects.select_related("category"),
        pk=pk
    )

    return render(request, "expenses/expense_detail.html", {
        "expense": expense,
    })