from django.contrib import admin
from .models import ExpenseCategory, Expense


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        "expense_number",
        "title",
        "category",
        "amount",
        "expense_date",
        "payment_method",
        "status",
    )
    search_fields = (
        "expense_number",
        "title",
        "paid_to",
        "reference",
    )
    list_filter = (
        "category",
        "payment_method",
        "status",
        "expense_date",
    )