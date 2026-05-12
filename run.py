import os
import django
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db.models import Q, Sum
from fees.models import FeeStructure, StudentInvoice, StudentInvoiceItem


invoice = StudentInvoice.objects.select_related(
    "student",
    "student__class_level",
    "academic_year",
    "term",
).get(invoice_number="INV-00001")

structures = FeeStructure.objects.filter(
    is_active=True,
    class_level=invoice.student.class_level,
    academic_year=invoice.academic_year,
).filter(
    Q(term=invoice.term) | Q(term__isnull=True)
)

created_count = 0

for structure in structures:
    item, created = StudentInvoiceItem.objects.get_or_create(
        invoice=invoice,
        category=structure.category,
        defaults={
            "description": f"{structure.category.name} fee",
            "amount": structure.amount,
        }
    )

    if created:
        created_count += 1

invoice.total_amount = invoice.items.aggregate(
    total=Sum("amount")
)["total"] or Decimal("0.00")

invoice.save(update_fields=["total_amount"])
invoice.refresh_status()

print("DONE")
print("Invoice:", invoice.invoice_number)
print("Created items:", created_count)
print("Total amount:", invoice.total_amount)
print("Status:", invoice.status)