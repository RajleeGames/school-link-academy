from django.contrib import admin
from .models import (
    FeeCategory,
    FeeStructure,
    StudentInvoice,
    StudentInvoiceItem,
    FeePayment,
)


@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = (
        "category",
        "academic_year",
        "term",
        "class_level",
        "amount",
        "is_required",
        "is_active",
    )
    list_filter = ("academic_year", "term", "class_level", "is_active")
    search_fields = ("category__name", "class_level__name")


class StudentInvoiceItemInline(admin.TabularInline):
    model = StudentInvoiceItem
    extra = 0


@admin.register(StudentInvoice)
class StudentInvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "student",
        "academic_year",
        "term",
        "total_amount",
        "discount_amount",
        "status",
        "invoice_date",
        "due_date",
    )
    list_filter = ("academic_year", "term", "status", "invoice_date")
    search_fields = (
        "invoice_number",
        "student__admission_number",
        "student__first_name",
        "student__last_name",
    )
    inlines = [StudentInvoiceItemInline]


@admin.register(StudentInvoiceItem)
class StudentInvoiceItemAdmin(admin.ModelAdmin):
    list_display = ("invoice", "category", "amount")
    search_fields = ("invoice__invoice_number", "category__name")


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = (
        "receipt_number",
        "invoice",
        "payment_date",
        "amount",
        "method",
        "status",
    )
    list_filter = ("method", "status", "payment_date")
    search_fields = (
        "receipt_number",
        "invoice__invoice_number",
        "invoice__student__admission_number",
        "invoice__student__first_name",
        "invoice__student__last_name",
    )