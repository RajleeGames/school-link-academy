from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from expenses.models import Expense, ExpenseCategory


def get_payroll_expense_category():
    category, created = ExpenseCategory.objects.get_or_create(
        name="Salaries / Payroll",
        defaults={
            "description": "Staff salary and payroll payments",
            "is_active": True,
        }
    )

    return category


def generate_expense_number():
    today = timezone.localdate()
    prefix = f"EXP-{today.strftime('%Y%m%d')}"

    last_expense = (
        Expense.objects
        .filter(expense_number__startswith=prefix)
        .order_by("-id")
        .first()
    )

    if not last_expense:
        return f"{prefix}-0001"

    try:
        last_number = int(last_expense.expense_number.split("-")[-1])
    except (ValueError, IndexError):
        last_number = 0

    next_number = last_number + 1

    return f"{prefix}-{next_number:04d}"


def normalize_payment_method(method):
    method = (method or "").strip().lower()

    if "bank" in method:
        return "bank"

    if "mobile" in method or "mpesa" in method or "m-pesa" in method or "tigopesa" in method or "airtel" in method:
        return "mobile_money"

    if "card" in method:
        return "card"

    if "cheque" in method or "check" in method:
        return "cheque"

    return "cash"


@transaction.atomic
def sync_payroll_expense(payroll_record, recorded_by=""):
    """
    Payroll and expenses rule:

    - Draft / Approved payroll: no paid expense yet.
    - Paid payroll: create or update expense.
    - Cancelled payroll: mark linked expense as cancelled.

    This keeps the finance dashboard correct.
    """

    status = (payroll_record.status or "").lower()

    if status != "paid":
        if payroll_record.expense:
            expense = payroll_record.expense
            expense.status = "cancelled"
            expense.description = (
                f"Cancelled payroll expense for {payroll_record.staff.full_name} - "
                f"{payroll_record.get_month_display()} {payroll_record.year}"
            )
            expense.save(update_fields=["status", "description"])

        return None

    amount = payroll_record.net_salary or Decimal("0.00")

    if amount <= 0:
        return None

    category = get_payroll_expense_category()

    staff_name = payroll_record.staff.full_name
    month_name = payroll_record.get_month_display()
    expense_date = payroll_record.payment_date or timezone.localdate()

    title = f"Salary Payment - {staff_name}"
    description = (
        f"Payroll salary payment for {staff_name} "
        f"for {month_name} {payroll_record.year}. "
        f"Basic: {payroll_record.basic_salary}, "
        f"Allowances: {payroll_record.total_allowances}, "
        f"Deductions: {payroll_record.total_deductions}, "
        f"Net: {payroll_record.net_salary}."
    )

    payment_method = normalize_payment_method(payroll_record.payment_method)

    if payroll_record.expense:
        expense = payroll_record.expense
        expense.category = category
        expense.title = title
        expense.description = description
        expense.amount = amount
        expense.expense_date = expense_date
        expense.payment_method = payment_method
        expense.reference = payroll_record.reference or ""
        expense.paid_to = staff_name
        expense.recorded_by = recorded_by or expense.recorded_by
        expense.status = "paid"
        expense.save()

        return expense

    expense = Expense.objects.create(
        category=category,
        expense_number=generate_expense_number(),
        title=title,
        description=description,
        amount=amount,
        expense_date=expense_date,
        payment_method=payment_method,
        reference=payroll_record.reference or "",
        paid_to=staff_name,
        recorded_by=recorded_by,
        status="paid",
    )

    payroll_record.expense = expense
    payroll_record.save(update_fields=["expense"])

    return expense