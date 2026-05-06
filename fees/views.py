from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.db.models import Q, Sum
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import permission_required
from academics.models import ClassLevel
from audit.utils import log_audit, model_to_dict_safe
from students.models import Student

from .forms import (
    FeeCategoryForm,
    FeePaymentForm,
    FeeStructureForm,
    StudentInvoiceForm,
    StudentInvoiceItemForm,
)
from .models import (
    FeeCategory,
    FeePayment,
    FeeStructure,
    StudentInvoice,
    StudentInvoiceItem,
)


def generate_invoice_number():
    last_invoice = StudentInvoice.objects.order_by("-id").first()
    next_id = 1 if not last_invoice else last_invoice.id + 1
    return f"INV-{next_id:05d}"


def generate_receipt_number():
    last_payment = FeePayment.objects.order_by("-id").first()
    next_id = 1 if not last_payment else last_payment.id + 1
    return f"REC-{next_id:05d}"


def to_decimal(value):
    try:
        return Decimal(str(value or "0"))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0.00")


def refresh_invoice(invoice):
    if hasattr(invoice, "refresh_status"):
        invoice.refresh_status()
    else:
        invoice.save()


def recalculate_invoice_total(invoice):
    total = invoice.items.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    invoice.total_amount = total
    invoice.save(update_fields=["total_amount"])
    refresh_invoice(invoice)


def safe_delete_object(request, obj, success_message, redirect_url, audit_message=None):
    object_repr = str(obj)
    old_values = model_to_dict_safe(obj)

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


def validate_payment_amount(request, invoice, amount, existing_payment=None):
    """
    For new payment:
      max allowed = invoice.balance

    For editing an existing payment:
      if that old payment was confirmed, its amount is already included in paid_amount.
      So max allowed = invoice.balance + old confirmed payment amount.
    """

    amount = to_decimal(amount)

    if amount <= 0:
        messages.error(request, "Payment amount must be greater than zero.")
        return False

    allowed_amount = invoice.balance

    if existing_payment and existing_payment.status == "confirmed":
        allowed_amount = invoice.balance + existing_payment.amount

    if amount > allowed_amount:
        messages.error(
            request,
            f"Payment cannot exceed remaining balance. Maximum allowed is TZS {allowed_amount:,.0f}."
        )
        return False

    return True


@permission_required("fees.view")
def fees_home(request):
    total_invoiced = StudentInvoice.objects.exclude(status="cancelled").aggregate(
        total=Sum("total_amount")
    )["total"] or Decimal("0.00")

    total_paid = FeePayment.objects.filter(status="confirmed").aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    outstanding = max(Decimal("0.00"), total_invoiced - total_paid)

    total_students_with_debt = StudentInvoice.objects.exclude(
        status__in=["paid", "cancelled"]
    ).values("student").distinct().count()

    recent_invoices = StudentInvoice.objects.select_related(
        "student",
        "academic_year",
        "term",
    ).order_by("-created_at")[:8]

    recent_payments = FeePayment.objects.select_related(
        "invoice",
        "invoice__student",
    ).order_by("-created_at")[:8]

    context = {
        "total_invoiced": total_invoiced,
        "total_paid": total_paid,
        "outstanding": outstanding,
        "total_students_with_debt": total_students_with_debt,
        "recent_invoices": recent_invoices,
        "recent_payments": recent_payments,
    }

    return render(request, "fees/home.html", context)


@permission_required("fees.setup")
def fee_category_list(request):
    categories = FeeCategory.objects.all()

    if request.method == "POST":
        form = FeeCategoryForm(request.POST)

        if form.is_valid():
            category = form.save()

            log_audit(
                request,
                action="create",
                obj=category,
                message=f"Created fee category {category.name}",
                old_values={},
                new_values=model_to_dict_safe(category),
            )

            messages.success(request, "Fee category saved successfully.")
            return redirect("fee_category_list")

        messages.error(request, "Please correct the category form.")
    else:
        form = FeeCategoryForm()

    return render(request, "fees/category_list.html", {
        "categories": categories,
        "form": form,
    })


@permission_required("fees.setup")
def fee_category_update(request, pk):
    category = get_object_or_404(FeeCategory, pk=pk)

    if request.method == "POST":
        old_values = model_to_dict_safe(category)
        form = FeeCategoryForm(request.POST, instance=category)

        if form.is_valid():
            category = form.save()

            log_audit(
                request,
                action="update",
                obj=category,
                message=f"Updated fee category {category.name}",
                old_values=old_values,
                new_values=model_to_dict_safe(category),
            )

            messages.success(request, "Fee category updated successfully.")
            return redirect("fee_category_list")

        messages.error(request, "Please correct the category form.")
    else:
        form = FeeCategoryForm(instance=category)

    return render(request, "fees/simple_fee_form.html", {
        "form": form,
        "title": "Update Fee Category",
        "button_text": "Update Category",
        "back_url": "fee_category_list",
    })


@permission_required("fees.setup")
def fee_category_delete(request, pk):
    category = get_object_or_404(FeeCategory, pk=pk)

    if request.method == "POST":
        return safe_delete_object(
            request,
            category,
            "Fee category deleted successfully.",
            "fee_category_list",
            audit_message=f"Deleted fee category {category.name}",
        )

    return redirect("fee_category_list")


@permission_required("fees.setup")
def fee_structure_list(request):
    structures = FeeStructure.objects.select_related(
        "category",
        "academic_year",
        "term",
        "class_level",
    ).all()

    if request.method == "POST":
        form = FeeStructureForm(request.POST)

        if form.is_valid():
            structure = form.save()

            log_audit(
                request,
                action="create",
                obj=structure,
                message=f"Created fee structure {structure}",
                old_values={},
                new_values=model_to_dict_safe(structure),
            )

            messages.success(request, "Fee structure saved successfully.")
            return redirect("fee_structure_list")

        messages.error(request, "Please correct the fee structure form.")
    else:
        form = FeeStructureForm()

    return render(request, "fees/structure_list.html", {
        "structures": structures,
        "form": form,
    })


@permission_required("fees.setup")
def fee_structure_update(request, pk):
    structure = get_object_or_404(FeeStructure, pk=pk)

    if request.method == "POST":
        old_values = model_to_dict_safe(structure)
        form = FeeStructureForm(request.POST, instance=structure)

        if form.is_valid():
            structure = form.save()

            log_audit(
                request,
                action="update",
                obj=structure,
                message=f"Updated fee structure {structure}",
                old_values=old_values,
                new_values=model_to_dict_safe(structure),
            )

            messages.success(request, "Fee structure updated successfully.")
            return redirect("fee_structure_list")

        messages.error(request, "Please correct the fee structure form.")
    else:
        form = FeeStructureForm(instance=structure)

    return render(request, "fees/simple_fee_form.html", {
        "form": form,
        "title": "Update Fee Structure",
        "button_text": "Update Structure",
        "back_url": "fee_structure_list",
    })


@permission_required("fees.setup")
def fee_structure_delete(request, pk):
    structure = get_object_or_404(FeeStructure, pk=pk)

    if request.method == "POST":
        return safe_delete_object(
            request,
            structure,
            "Fee structure deleted successfully.",
            "fee_structure_list",
            audit_message=f"Deleted fee structure {structure}",
        )

    return redirect("fee_structure_list")


@permission_required("invoices.view")
def invoice_list(request):
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()
    class_filter = request.GET.get("class", "").strip()

    invoices = StudentInvoice.objects.select_related(
        "student",
        "student__class_level",
        "student__stream",
        "academic_year",
        "term",
    ).all()

    if query:
        invoices = invoices.filter(
            Q(invoice_number__icontains=query) |
            Q(student__admission_number__icontains=query) |
            Q(student__first_name__icontains=query) |
            Q(student__middle_name__icontains=query) |
            Q(student__last_name__icontains=query)
        )

    if status_filter:
        invoices = invoices.filter(status=status_filter)

    if class_filter:
        invoices = invoices.filter(student__class_level_id=class_filter)

    context = {
        "invoices": invoices,
        "query": query,
        "status_filter": status_filter,
        "class_filter": class_filter,
        "classes": ClassLevel.objects.filter(is_active=True),
        "status_choices": StudentInvoice.STATUS_CHOICES,
    }

    return render(request, "fees/invoice_list.html", context)


@permission_required("invoices.view")
def debtor_list(request):
    query = request.GET.get("q", "").strip()
    class_filter = request.GET.get("class", "").strip()

    invoices = StudentInvoice.objects.select_related(
        "student",
        "student__class_level",
        "student__stream",
        "academic_year",
        "term",
    ).exclude(
        status__in=["paid", "cancelled"]
    )

    if query:
        invoices = invoices.filter(
            Q(invoice_number__icontains=query) |
            Q(student__admission_number__icontains=query) |
            Q(student__first_name__icontains=query) |
            Q(student__middle_name__icontains=query) |
            Q(student__last_name__icontains=query) |
            Q(student__parent_guardian__full_name__icontains=query) |
            Q(student__parent_guardian__phone__icontains=query)
        )

    if class_filter:
        invoices = invoices.filter(student__class_level_id=class_filter)

    grouped = {}

    for invoice in invoices:
        student = invoice.student

        if student.id not in grouped:
            grouped[student.id] = {
                "student": student,
                "invoice_count": 0,
                "total_payable": Decimal("0.00"),
                "total_paid": Decimal("0.00"),
                "total_balance": Decimal("0.00"),
                "latest_invoice": invoice,
            }

        grouped[student.id]["invoice_count"] += 1
        grouped[student.id]["total_payable"] += invoice.payable_amount
        grouped[student.id]["total_paid"] += invoice.paid_amount
        grouped[student.id]["total_balance"] += invoice.balance

        if invoice.invoice_date > grouped[student.id]["latest_invoice"].invoice_date:
            grouped[student.id]["latest_invoice"] = invoice

    debtor_rows = list(grouped.values())
    debtor_rows.sort(key=lambda row: row["total_balance"], reverse=True)

    return render(request, "fees/debtor_list.html", {
        "debtor_rows": debtor_rows,
        "query": query,
        "class_filter": class_filter,
        "classes": ClassLevel.objects.filter(is_active=True),
    })


@permission_required("invoices.manage")
def invoice_create(request):
    if request.method == "POST":
        form = StudentInvoiceForm(request.POST)

        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.status = "unpaid"
            invoice.save()
            refresh_invoice(invoice)

            log_audit(
                request,
                action="create",
                obj=invoice,
                message=f"Created invoice {invoice.invoice_number} for {invoice.student.full_name}",
                old_values={},
                new_values=model_to_dict_safe(invoice),
            )

            messages.success(request, "Invoice created successfully.")
            return redirect("invoice_detail", pk=invoice.pk)

        messages.error(request, "Please correct the invoice form.")
    else:
        form = StudentInvoiceForm(
            initial={
                "invoice_number": generate_invoice_number(),
                "invoice_date": timezone.now().date(),
                "discount_amount": 0,
                "total_amount": 0,
            }
        )

    return render(request, "fees/invoice_form.html", {
        "form": form,
        "title": "Create Invoice",
        "button_text": "Save Invoice",
        "is_update": False,
    })


@permission_required("invoices.manage")
def invoice_update(request, pk):
    invoice = get_object_or_404(StudentInvoice, pk=pk)

    if invoice.status == "cancelled":
        messages.error(request, "Cancelled invoice cannot be edited.")
        return redirect("invoice_detail", pk=invoice.pk)

    if request.method == "POST":
        old_values = model_to_dict_safe(invoice)
        form = StudentInvoiceForm(request.POST, instance=invoice)

        if form.is_valid():
            updated_invoice = form.save()
            refresh_invoice(updated_invoice)

            log_audit(
                request,
                action="update",
                obj=updated_invoice,
                message=f"Updated invoice {updated_invoice.invoice_number}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_invoice),
            )

            messages.success(request, "Invoice updated successfully.")
            return redirect("invoice_detail", pk=updated_invoice.pk)

        messages.error(request, "Please correct the invoice form.")
    else:
        form = StudentInvoiceForm(instance=invoice)

    return render(request, "fees/invoice_form.html", {
        "form": form,
        "invoice": invoice,
        "title": "Update Invoice",
        "button_text": "Update Invoice",
        "is_update": True,
    })


@permission_required("invoices.manage")
def invoice_delete(request, pk):
    invoice = get_object_or_404(StudentInvoice, pk=pk)

    if invoice.payments.exists():
        messages.error(
            request,
            "This invoice has payments. Delete or cancel payments first, or keep the invoice for records."
        )
        return redirect("invoice_detail", pk=invoice.pk)

    if request.method == "POST":
        return safe_delete_object(
            request,
            invoice,
            "Invoice deleted successfully.",
            "invoice_list",
            audit_message=f"Deleted invoice {invoice.invoice_number}",
        )

    return redirect("invoice_list")


@permission_required("invoices.view")
def invoice_detail(request, pk):
    invoice = get_object_or_404(
        StudentInvoice.objects.select_related(
            "student",
            "student__class_level",
            "student__stream",
            "academic_year",
            "term",
        ),
        pk=pk,
    )

    items = invoice.items.select_related("category").all()
    payments = invoice.payments.all()
    categories = FeeCategory.objects.filter(is_active=True)

    return render(request, "fees/invoice_detail.html", {
        "invoice": invoice,
        "items": items,
        "payments": payments,
        "categories": categories,
    })


@permission_required("invoices.manage")
def invoice_add_item(request, pk):
    invoice = get_object_or_404(StudentInvoice, pk=pk)

    if invoice.status == "cancelled":
        messages.error(request, "Cannot add items to a cancelled invoice.")
        return redirect("invoice_detail", pk=invoice.pk)

    if request.method == "POST":
        form = StudentInvoiceItemForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.invoice = invoice
            item.save()

            recalculate_invoice_total(invoice)

            log_audit(
                request,
                action="create",
                obj=item,
                message=f"Added item to invoice {invoice.invoice_number}",
                old_values={},
                new_values=model_to_dict_safe(item),
            )

            messages.success(request, "Invoice item added successfully.")
        else:
            messages.error(request, "Please correct the invoice item form.")

    return redirect("invoice_detail", pk=invoice.pk)


@permission_required("invoices.manage")
def invoice_item_update(request, pk):
    item = get_object_or_404(
        StudentInvoiceItem.objects.select_related("invoice"),
        pk=pk
    )

    invoice = item.invoice

    if invoice.status == "cancelled":
        messages.error(request, "Cannot edit items on a cancelled invoice.")
        return redirect("invoice_detail", pk=invoice.pk)

    if request.method == "POST":
        old_values = model_to_dict_safe(item)
        form = StudentInvoiceItemForm(request.POST, instance=item)

        if form.is_valid():
            item = form.save()
            recalculate_invoice_total(invoice)

            log_audit(
                request,
                action="update",
                obj=item,
                message=f"Updated item on invoice {invoice.invoice_number}",
                old_values=old_values,
                new_values=model_to_dict_safe(item),
            )

            messages.success(request, "Invoice item updated successfully.")
            return redirect("invoice_detail", pk=invoice.pk)

        messages.error(request, "Please correct the invoice item form.")
    else:
        form = StudentInvoiceItemForm(instance=item)

    return render(request, "fees/simple_fee_form.html", {
        "form": form,
        "title": "Update Invoice Item",
        "button_text": "Update Item",
        "back_url": "invoice_detail",
        "back_pk": invoice.pk,
    })


@permission_required("invoices.manage")
def invoice_item_delete(request, pk):
    item = get_object_or_404(
        StudentInvoiceItem.objects.select_related("invoice"),
        pk=pk
    )

    invoice = item.invoice

    if invoice.status == "cancelled":
        messages.error(request, "Cannot delete items from a cancelled invoice.")
        return redirect("invoice_detail", pk=invoice.pk)

    if request.method == "POST":
        old_values = model_to_dict_safe(item)
        item_repr = str(item)

        log_audit(
            request,
            action="delete",
            obj=item,
            message=f"Deleted item from invoice {invoice.invoice_number}: {item_repr}",
            old_values=old_values,
            new_values={},
        )

        item.delete()
        recalculate_invoice_total(invoice)
        messages.success(request, "Invoice item deleted successfully.")

    return redirect("invoice_detail", pk=invoice.pk)


@permission_required("payments.view")
def payment_list(request):
    query = request.GET.get("q", "").strip()

    payments = FeePayment.objects.select_related(
        "invoice",
        "invoice__student",
        "invoice__student__class_level",
        "invoice__student__stream",
    ).all()

    if query:
        payments = payments.filter(
            Q(receipt_number__icontains=query) |
            Q(invoice__invoice_number__icontains=query) |
            Q(invoice__student__admission_number__icontains=query) |
            Q(invoice__student__first_name__icontains=query) |
            Q(invoice__student__middle_name__icontains=query) |
            Q(invoice__student__last_name__icontains=query)
        )

    grouped = {}

    for payment in payments:
        student = payment.invoice.student

        if student.id not in grouped:
            grouped[student.id] = {
                "student": student,
                "payment_count": 0,
                "confirmed_total": Decimal("0.00"),
                "pending_total": Decimal("0.00"),
                "cancelled_total": Decimal("0.00"),
                "last_payment": payment,
            }

        grouped[student.id]["payment_count"] += 1

        if payment.status == "confirmed":
            grouped[student.id]["confirmed_total"] += payment.amount
        elif payment.status == "pending":
            grouped[student.id]["pending_total"] += payment.amount
        elif payment.status == "cancelled":
            grouped[student.id]["cancelled_total"] += payment.amount

        if payment.payment_date > grouped[student.id]["last_payment"].payment_date:
            grouped[student.id]["last_payment"] = payment

    payment_rows = list(grouped.values())

    payment_rows.sort(
        key=lambda row: (
            row["student"].class_level.order,
            row["student"].first_name,
            row["student"].last_name,
        )
    )

    return render(request, "fees/payment_list.html", {
        "payment_rows": payment_rows,
        "query": query,
    })


@permission_required("payments.view")
def student_payment_history(request, student_id):
    student = get_object_or_404(
        Student.objects.select_related(
            "class_level",
            "stream",
            "parent_guardian",
        ),
        pk=student_id
    )

    payments = FeePayment.objects.select_related(
        "invoice",
        "invoice__academic_year",
        "invoice__term",
    ).filter(
        invoice__student=student
    ).order_by("-payment_date", "-id")

    invoices = StudentInvoice.objects.select_related(
        "academic_year",
        "term",
    ).filter(
        student=student
    ).order_by("-invoice_date", "-id")

    confirmed_total = payments.filter(status="confirmed").aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    pending_total = payments.filter(status="pending").aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    outstanding_balance = Decimal("0.00")

    for invoice in invoices.exclude(status="cancelled"):
        outstanding_balance += invoice.balance

    return render(request, "fees/student_payment_history.html", {
        "student": student,
        "payments": payments,
        "invoices": invoices,
        "confirmed_total": confirmed_total,
        "pending_total": pending_total,
        "outstanding_balance": outstanding_balance,
    })


@permission_required("payments.manage")
def payment_create(request):
    invoice_id = request.GET.get("invoice")

    initial = {
        "receipt_number": generate_receipt_number(),
        "payment_date": timezone.now().date(),
        "status": "confirmed",
    }

    selected_invoice = None

    if invoice_id:
        selected_invoice = get_object_or_404(StudentInvoice, pk=invoice_id)
        initial["invoice"] = selected_invoice
        initial["amount"] = selected_invoice.balance

    if request.method == "POST":
        form = FeePaymentForm(request.POST)

        if form.is_valid():
            payment = form.save(commit=False)
            amount = form.cleaned_data["amount"]

            if payment.invoice.status == "cancelled":
                messages.error(request, "You cannot record payment for a cancelled invoice.")
                return render(request, "fees/payment_form.html", {
                    "form": form,
                    "title": "Record Payment",
                    "button_text": "Save Payment",
                    "selected_invoice": payment.invoice,
                    "remaining_balance": payment.invoice.balance,
                    "is_update": False,
                })

            if not validate_payment_amount(request, payment.invoice, amount):
                return render(request, "fees/payment_form.html", {
                    "form": form,
                    "title": "Record Payment",
                    "button_text": "Save Payment",
                    "selected_invoice": payment.invoice,
                    "remaining_balance": payment.invoice.balance,
                    "is_update": False,
                })

            payment.save()
            refresh_invoice(payment.invoice)

            log_audit(
                request,
                action="create",
                obj=payment,
                message=(
                    f"Recorded payment {payment.receipt_number} "
                    f"for invoice {payment.invoice.invoice_number}"
                ),
                old_values={},
                new_values=model_to_dict_safe(payment),
            )

            messages.success(request, "Payment recorded successfully.")
            return redirect("receipt_detail", pk=payment.pk)

        messages.error(request, "Please correct the payment form.")
    else:
        form = FeePaymentForm(initial=initial)

    return render(request, "fees/payment_form.html", {
        "form": form,
        "title": "Record Payment",
        "button_text": "Save Payment",
        "selected_invoice": selected_invoice,
        "remaining_balance": selected_invoice.balance if selected_invoice else None,
        "is_update": False,
    })


@permission_required("payments.manage")
def payment_update(request, pk):
    payment = get_object_or_404(
        FeePayment.objects.select_related("invoice"),
        pk=pk
    )

    old_invoice = payment.invoice

    if request.method == "POST":
        old_values = model_to_dict_safe(payment)
        form = FeePaymentForm(request.POST, instance=payment)

        if form.is_valid():
            updated_payment = form.save(commit=False)
            amount = form.cleaned_data["amount"]

            if updated_payment.invoice.status == "cancelled":
                messages.error(request, "You cannot record payment for a cancelled invoice.")
                return render(request, "fees/payment_form.html", {
                    "form": form,
                    "payment": payment,
                    "title": "Update Payment",
                    "button_text": "Update Payment",
                    "selected_invoice": updated_payment.invoice,
                    "remaining_balance": updated_payment.invoice.balance,
                    "is_update": True,
                })

            if not validate_payment_amount(
                request,
                updated_payment.invoice,
                amount,
                existing_payment=payment if old_invoice.pk == updated_payment.invoice.pk else None
            ):
                return render(request, "fees/payment_form.html", {
                    "form": form,
                    "payment": payment,
                    "title": "Update Payment",
                    "button_text": "Update Payment",
                    "selected_invoice": updated_payment.invoice,
                    "remaining_balance": updated_payment.invoice.balance,
                    "is_update": True,
                })

            updated_payment.save()
            refresh_invoice(old_invoice)
            refresh_invoice(updated_payment.invoice)

            log_audit(
                request,
                action="update",
                obj=updated_payment,
                message=(
                    f"Updated payment {updated_payment.receipt_number} "
                    f"for invoice {updated_payment.invoice.invoice_number}"
                ),
                old_values=old_values,
                new_values=model_to_dict_safe(updated_payment),
            )

            messages.success(request, "Payment updated successfully.")
            return redirect("receipt_detail", pk=updated_payment.pk)

        messages.error(request, "Please correct the payment form.")
    else:
        form = FeePaymentForm(instance=payment)

    allowed_amount = payment.invoice.balance

    if payment.status == "confirmed":
        allowed_amount = payment.invoice.balance + payment.amount

    return render(request, "fees/payment_form.html", {
        "form": form,
        "payment": payment,
        "title": "Update Payment",
        "button_text": "Update Payment",
        "selected_invoice": payment.invoice,
        "remaining_balance": allowed_amount,
        "is_update": True,
    })


@permission_required("payments.manage")
def payment_delete(request, pk):
    payment = get_object_or_404(
        FeePayment.objects.select_related("invoice"),
        pk=pk
    )

    invoice = payment.invoice

    if request.method == "POST":
        old_values = model_to_dict_safe(payment)

        log_audit(
            request,
            action="delete",
            obj=payment,
            message=(
                f"Deleted payment {payment.receipt_number} "
                f"from invoice {invoice.invoice_number}"
            ),
            old_values=old_values,
            new_values={},
        )

        payment.delete()
        refresh_invoice(invoice)
        messages.success(request, "Payment deleted successfully.")

    return redirect("payment_list")


@permission_required("payments.view")
def receipt_detail(request, pk):
    payment = get_object_or_404(
        FeePayment.objects.select_related(
            "invoice",
            "invoice__student",
            "invoice__student__class_level",
            "invoice__student__stream",
        ),
        pk=pk,
    )

    return render(request, "fees/receipt_detail.html", {
        "payment": payment,
    })