from decimal import Decimal
from django.db.models import Q, Sum

from fees.models import FeeStructure, StudentInvoice, StudentInvoiceItem


def sync_invoice_items_from_fee_structure(invoice):
    if not invoice.student_id or not invoice.academic_year_id:
        return 0

    structures = (
        FeeStructure.objects
        .select_related("category", "academic_year", "term", "class_level")
        .filter(
            is_active=True,
            class_level=invoice.student.class_level,
            academic_year=invoice.academic_year,
        )
        .filter(
            Q(term=invoice.term) | Q(term__isnull=True)
        )
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

    total = invoice.items.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    invoice.total_amount = total
    invoice.save(update_fields=["total_amount"])

    invoice.refresh_status()

    return created_count


updated_invoices = 0
created_items = 0
skipped_cancelled = 0
no_matching_structure = 0
already_has_items = 0

invoices = (
    StudentInvoice.objects
    .select_related(
        "student",
        "student__class_level",
        "academic_year",
        "term",
    )
    .prefetch_related("items")
    .all()
)

for invoice in invoices:
    if invoice.status == "cancelled":
        skipped_cancelled += 1
        continue

    before_count = invoice.items.count()

    if before_count > 0:
        already_has_items += 1

    added = sync_invoice_items_from_fee_structure(invoice)

    if added > 0:
        updated_invoices += 1
        created_items += added

    if before_count == 0 and added == 0:
        no_matching_structure += 1

print("DONE")
print("Total invoices checked:", invoices.count())
print("Updated invoices:", updated_invoices)
print("Created invoice items:", created_items)
print("Already had invoice items:", already_has_items)
print("Skipped cancelled invoices:", skipped_cancelled)
print("Invoices with no matching fee structure:", no_matching_structure)
