from decimal import Decimal

from django.db.models import Q, Sum

from .models import FeeStructure, StudentInvoiceItem, FeePayment


def money(value):
    return value or Decimal("0.00")


def recalculate_invoice_total(invoice):
    total = invoice.items.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    invoice.total_amount = total
    invoice.save(update_fields=["total_amount"])
    invoice.refresh_status()
    return invoice


def sync_invoice_items_from_fee_structure(invoice):
    """
    Automatically creates invoice items from FeeStructure.

    It picks fees by:
    - student's class
    - selected academic year
    - selected term
    - active fee structures only

    It avoids duplicate category items.
    """

    if not invoice.student_id or not invoice.academic_year_id:
        return invoice

    structures = FeeStructure.objects.select_related(
        "category",
        "academic_year",
        "term",
        "class_level",
    ).filter(
        is_active=True,
        class_level=invoice.student.class_level,
        academic_year=invoice.academic_year,
    ).filter(
        Q(term=invoice.term) | Q(term__isnull=True)
    )

    created_count = 0

    for structure in structures:
        exists = StudentInvoiceItem.objects.filter(
            invoice=invoice,
            category=structure.category,
        ).exists()

        if exists:
            continue

        StudentInvoiceItem.objects.create(
            invoice=invoice,
            category=structure.category,
            description=f"{structure.category.name} fee",
            amount=structure.amount,
        )

        created_count += 1

    recalculate_invoice_total(invoice)

    return invoice


def build_invoice_fee_breakdown(invoice):
    """
    Builds classic breakdown:

    Tuition  Required  Paid  Balance  Status
    Books    Required  Paid  Balance  Status

    Payments linked to fee_item are counted exactly.
    Old payments without fee_item are applied from first item to last item.
    """

    items = list(
        invoice.items.select_related("category").order_by("category__name", "id")
    )

    confirmed_payments = invoice.payments.filter(status="confirmed")

    unallocated_paid = confirmed_payments.filter(
        fee_item__isnull=True
    ).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    breakdown = []

    for item in items:
        required = money(item.amount)

        direct_paid = confirmed_payments.filter(
            fee_item=item
        ).aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

        auto_paid = Decimal("0.00")

        if unallocated_paid > 0:
            remaining_after_direct = max(Decimal("0.00"), required - direct_paid)

            if unallocated_paid >= remaining_after_direct:
                auto_paid = remaining_after_direct
                unallocated_paid -= remaining_after_direct
            else:
                auto_paid = unallocated_paid
                unallocated_paid = Decimal("0.00")

        paid = direct_paid + auto_paid
        balance = max(Decimal("0.00"), required - paid)

        if balance <= 0 and required > 0:
            status = "paid"
        elif paid > 0:
            status = "partial"
        else:
            status = "unpaid"

        breakdown.append({
            "item": item,
            "category": item.category.name if item.category else "Fee Item",
            "description": item.description,
            "required": required,
            "paid": paid,
            "balance": balance,
            "status": status,
        })

    return breakdown


def get_fee_item_balance(fee_item, exclude_payment=None):
    confirmed_payments = FeePayment.objects.filter(
        fee_item=fee_item,
        status="confirmed",
    )

    if exclude_payment:
        confirmed_payments = confirmed_payments.exclude(pk=exclude_payment.pk)

    paid = confirmed_payments.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    return max(Decimal("0.00"), money(fee_item.amount) - paid)