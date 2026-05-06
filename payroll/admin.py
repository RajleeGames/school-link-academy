from django.contrib import admin

from .models import PayrollRecord, SalaryStructure


@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = (
        "staff",
        "basic_salary",
        "total_allowances",
        "total_deductions",
        "net_salary",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = (
        "staff__first_name",
        "staff__middle_name",
        "staff__last_name",
        "staff__staff_id",
    )
    list_select_related = ("staff",)


@admin.register(PayrollRecord)
class PayrollRecordAdmin(admin.ModelAdmin):
    list_display = (
        "staff",
        "month",
        "year",
        "basic_salary",
        "total_allowances",
        "total_deductions",
        "net_salary",
        "status",
    )
    list_filter = ("status", "month", "year")
    search_fields = (
        "staff__first_name",
        "staff__middle_name",
        "staff__last_name",
        "staff__staff_id",
        "reference",
    )
    list_select_related = ("staff",)