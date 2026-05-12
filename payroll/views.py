from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import (
    can_view_payroll_record,
    payroll_admin_required,
    permission_required,
    user_staff_profile,
)
from audit.utils import log_audit, model_to_dict_safe

from .forms import PayrollGenerateForm, PayrollRecordForm, SalaryStructureForm
from .models import PayrollRecord, SalaryStructure
from .utils import sync_payroll_expense


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


def calculate_net_salary(payroll):
    return (
        payroll.basic_salary
        + payroll.total_allowances
        - payroll.total_deductions
    )


def salary_structure_audit_message(structure, prefix):
    return f"{prefix} salary structure for {structure.staff.full_name}"


def payroll_record_audit_message(record, prefix):
    return (
        f"{prefix} payroll record for {record.staff.full_name} "
        f"- {record.get_month_display()} {record.year}"
    )


def payroll_record_safe_values(record):
    data = model_to_dict_safe(record)

    if record.expense:
        data["expense"] = str(record.expense)
        data["expense_id"] = str(record.expense_id)
    else:
        data["expense"] = ""
        data["expense_id"] = ""

    return data


def payroll_sync_recorded_by(request):
    if request and request.user.is_authenticated:
        return request.user.username

    return ""


def sync_payroll_expense_with_audit(request, payroll):
    expense = sync_payroll_expense(
        payroll,
        recorded_by=payroll_sync_recorded_by(request),
    )

    if expense:
        log_audit(
            request,
            action="pay",
            obj=payroll,
            message=(
                f"Payroll expense synced for {payroll.staff.full_name} "
                f"- {payroll.get_month_display()} {payroll.year}"
            ),
            old_values={},
            new_values={
                "staff": str(payroll.staff),
                "month": payroll.get_month_display(),
                "year": str(payroll.year),
                "net_salary": str(payroll.net_salary),
                "expense": str(expense),
                "expense_number": expense.expense_number,
                "expense_status": expense.status,
            },
        )

    return expense


@permission_required("payroll.view")
def payroll_home(request):
    current_year = timezone.localdate().year
    current_month = timezone.localdate().month

    is_payroll_admin = payroll_admin_required(request.user)
    staff_profile = user_staff_profile(request.user)

    structures = SalaryStructure.objects.select_related("staff")
    records = PayrollRecord.objects.select_related("staff", "expense")

    if not is_payroll_admin:
        if staff_profile:
            structures = structures.filter(staff=staff_profile)
            records = records.filter(staff=staff_profile)
        else:
            structures = structures.none()
            records = records.none()

    total_structures = structures.count()
    active_structures = structures.filter(is_active=True).count()

    current_records = records.filter(
        month=current_month,
        year=current_year
    )

    current_payroll_count = current_records.count()
    current_payroll_total = current_records.aggregate(
        total=Sum("net_salary")
    )["total"] or 0

    paid_count = current_records.filter(status="paid").count()

    recent_records = records.order_by("-id")[:8]

    status_summary = records.values("status").annotate(
        count=Count("id"),
        total=Sum("net_salary")
    ).order_by("status")

    context = {
        "total_structures": total_structures,
        "active_structures": active_structures,
        "current_payroll_count": current_payroll_count,
        "current_payroll_total": current_payroll_total,
        "paid_count": paid_count,
        "recent_records": recent_records,
        "status_summary": status_summary,
        "can_manage_payroll": is_payroll_admin,
    }

    return render(request, "payroll/home.html", context)


@permission_required("payroll.view")
def salary_structure_list(request):
    structures = SalaryStructure.objects.select_related("staff")

    is_payroll_admin = payroll_admin_required(request.user)
    staff_profile = user_staff_profile(request.user)

    if not is_payroll_admin:
        if staff_profile:
            structures = structures.filter(staff=staff_profile)
        else:
            structures = structures.none()

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        structures = structures.filter(
            Q(staff__first_name__icontains=search)
            | Q(staff__middle_name__icontains=search)
            | Q(staff__last_name__icontains=search)
            | Q(staff__staff_id__icontains=search)
            | Q(staff__phone__icontains=search)
        )

    if status == "active":
        structures = structures.filter(is_active=True)

    if status == "inactive":
        structures = structures.filter(is_active=False)

    context = {
        "structures": structures,
        "search": search,
        "selected_status": status,
        "can_manage_payroll": is_payroll_admin,
    }

    return render(request, "payroll/salary_structure_list.html", context)


@permission_required("payroll.manage")
def salary_structure_create(request):
    if request.method == "POST":
        form = SalaryStructureForm(request.POST)

        if form.is_valid():
            structure = form.save()

            log_audit(
                request,
                action="create",
                obj=structure,
                message=salary_structure_audit_message(structure, "Created"),
                old_values={},
                new_values=model_to_dict_safe(structure),
            )

            messages.success(request, "Salary structure added successfully.")
            return redirect("salary_structure_list")

        messages.error(request, "Please correct the salary structure form.")
    else:
        form = SalaryStructureForm()

    return render(request, "payroll/simple_form.html", {
        "form": form,
        "title": "Add Salary Structure",
        "button_text": "Save Salary Structure",
        "back_url": "salary_structure_list",
    })


@permission_required("payroll.manage")
def salary_structure_update(request, pk):
    structure = get_object_or_404(SalaryStructure, pk=pk)

    if request.method == "POST":
        old_values = model_to_dict_safe(structure)
        form = SalaryStructureForm(request.POST, instance=structure)

        if form.is_valid():
            structure = form.save()

            log_audit(
                request,
                action="update",
                obj=structure,
                message=salary_structure_audit_message(structure, "Updated"),
                old_values=old_values,
                new_values=model_to_dict_safe(structure),
            )

            messages.success(request, "Salary structure updated successfully.")
            return redirect("salary_structure_list")

        messages.error(request, "Please correct the salary structure form.")
    else:
        form = SalaryStructureForm(instance=structure)

    return render(request, "payroll/simple_form.html", {
        "form": form,
        "title": "Edit Salary Structure",
        "button_text": "Update Salary Structure",
        "back_url": "salary_structure_list",
    })


@permission_required("payroll.manage")
def salary_structure_delete(request, pk):
    structure = get_object_or_404(SalaryStructure, pk=pk)

    payroll_exists = PayrollRecord.objects.filter(staff=structure.staff).exists()

    if payroll_exists:
        messages.error(
            request,
            "This staff member already has payroll records. Do not delete the salary structure. "
            "Mark it inactive instead."
        )
        return redirect("salary_structure_list")

    if request.method == "POST":
        return safe_delete_object(
            request,
            structure,
            "Salary structure deleted successfully.",
            "salary_structure_list",
            audit_message=salary_structure_audit_message(structure, "Deleted"),
        )

    return redirect("salary_structure_list")


@permission_required("payroll.view")
def payroll_record_list(request):
    records = PayrollRecord.objects.select_related("staff", "expense")

    is_payroll_admin = payroll_admin_required(request.user)
    staff_profile = user_staff_profile(request.user)

    if not is_payroll_admin:
        if staff_profile:
            records = records.filter(staff=staff_profile)
        else:
            records = records.none()

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()
    month = request.GET.get("month", "").strip()
    year = request.GET.get("year", "").strip()

    if search:
        records = records.filter(
            Q(staff__first_name__icontains=search)
            | Q(staff__middle_name__icontains=search)
            | Q(staff__last_name__icontains=search)
            | Q(staff__staff_id__icontains=search)
            | Q(staff__phone__icontains=search)
            | Q(reference__icontains=search)
            | Q(expense__expense_number__icontains=search)
        )

    if status:
        records = records.filter(status=status)

    if month:
        records = records.filter(month=month)

    if year:
        records = records.filter(year=year)

    context = {
        "records": records,
        "search": search,
        "selected_status": status,
        "selected_month": month,
        "selected_year": year,
        "month_choices": PayrollRecord.MONTH_CHOICES,
        "can_manage_payroll": is_payroll_admin,
    }

    return render(request, "payroll/payroll_record_list.html", context)


@permission_required("payroll.manage")
def payroll_record_create(request):
    if request.method == "POST":
        form = PayrollRecordForm(request.POST)

        if form.is_valid():
            payroll = form.save(commit=False)
            payroll.net_salary = calculate_net_salary(payroll)
            payroll.save()

            expense = sync_payroll_expense_with_audit(request, payroll)

            new_values = payroll_record_safe_values(payroll)

            if expense:
                new_values["synced_expense"] = str(expense)
                new_values["synced_expense_number"] = expense.expense_number

            log_audit(
                request,
                action="create",
                obj=payroll,
                message=payroll_record_audit_message(payroll, "Created"),
                old_values={},
                new_values=new_values,
            )

            if payroll.status == "paid" and expense:
                messages.success(
                    request,
                    "Payroll record added successfully and salary expense was created."
                )
            else:
                messages.success(request, "Payroll record added successfully.")

            return redirect("payroll_record_detail", pk=payroll.pk)

        messages.error(request, "Please correct the payroll record form.")
    else:
        form = PayrollRecordForm()

    return render(request, "payroll/simple_form.html", {
        "form": form,
        "title": "Add Payroll Record",
        "button_text": "Save Payroll Record",
        "back_url": "payroll_record_list",
    })


@permission_required("payroll.manage")
def payroll_record_update(request, pk):
    record = get_object_or_404(
        PayrollRecord.objects.select_related("staff", "expense"),
        pk=pk
    )

    if request.method == "POST":
        old_values = payroll_record_safe_values(record)
        form = PayrollRecordForm(request.POST, instance=record)

        if form.is_valid():
            payroll = form.save(commit=False)
            payroll.net_salary = calculate_net_salary(payroll)
            payroll.save()

            expense = sync_payroll_expense_with_audit(request, payroll)

            new_values = payroll_record_safe_values(payroll)

            if expense:
                new_values["synced_expense"] = str(expense)
                new_values["synced_expense_number"] = expense.expense_number

            log_audit(
                request,
                action="update",
                obj=payroll,
                message=payroll_record_audit_message(payroll, "Updated"),
                old_values=old_values,
                new_values=new_values,
            )

            if payroll.status == "paid" and expense:
                messages.success(
                    request,
                    "Payroll record updated successfully and salary expense was synced."
                )
            elif payroll.status != "paid":
                messages.success(
                    request,
                    "Payroll record updated successfully. No paid expense is created until status is Paid."
                )
            else:
                messages.success(request, "Payroll record updated successfully.")

            return redirect("payroll_record_detail", pk=payroll.pk)

        messages.error(request, "Please correct the payroll record form.")
    else:
        form = PayrollRecordForm(instance=record)

    return render(request, "payroll/simple_form.html", {
        "form": form,
        "title": "Edit Payroll Record",
        "button_text": "Update Payroll Record",
        "back_url": "payroll_record_list",
    })


@permission_required("payroll.manage")
def payroll_record_delete(request, pk):
    record = get_object_or_404(
        PayrollRecord.objects.select_related("staff", "expense"),
        pk=pk
    )

    if record.status == "paid":
        messages.error(
            request,
            "This payroll record is already paid. Do not delete paid payroll. "
            "Change status to cancelled only if needed."
        )
        return redirect("payroll_record_detail", pk=record.pk)

    if request.method == "POST":
        return safe_delete_object(
            request,
            record,
            "Payroll record deleted successfully.",
            "payroll_record_list",
            audit_message=payroll_record_audit_message(record, "Deleted"),
        )

    return redirect("payroll_record_list")


@permission_required("payroll.view")
def payroll_record_detail(request, pk):
    record = get_object_or_404(
        PayrollRecord.objects.select_related("staff", "expense"),
        pk=pk
    )

    if not can_view_payroll_record(request.user, record):
        messages.error(request, "You are not allowed to view this payslip.")
        return render(
            request,
            "accounts/access_denied.html",
            {"permission_code": "payroll.view.own"},
            status=403,
        )

    return render(request, "payroll/payroll_record_detail.html", {
        "record": record,
        "can_manage_payroll": payroll_admin_required(request.user),
    })


@permission_required("payroll.manage")
def payroll_generate(request):
    if request.method == "POST":
        form = PayrollGenerateForm(request.POST)

        if form.is_valid():
            month = int(form.cleaned_data["month"])
            year = int(form.cleaned_data["year"])

            created_count = 0
            skipped_count = 0
            created_records = []

            structures = SalaryStructure.objects.select_related(
                "staff"
            ).filter(is_active=True)

            for structure in structures:
                exists = PayrollRecord.objects.filter(
                    staff=structure.staff,
                    month=month,
                    year=year
                ).exists()

                if exists:
                    skipped_count += 1
                    continue

                payroll = PayrollRecord.objects.create(
                    staff=structure.staff,
                    month=month,
                    year=year,
                    basic_salary=structure.basic_salary,
                    total_allowances=structure.total_allowances,
                    total_deductions=structure.total_deductions,
                    net_salary=structure.net_salary,
                    status="draft",
                )

                log_audit(
                    request,
                    action="create",
                    obj=payroll,
                    message=payroll_record_audit_message(payroll, "Generated"),
                    old_values={},
                    new_values=model_to_dict_safe(payroll),
                )

                created_records.append(str(payroll))
                created_count += 1

            log_audit(
                request,
                action="generate",
                obj=None,
                app_label="payroll",
                model_name="payrollrecord",
                object_repr=f"Payroll {month}/{year}",
                message=(
                    f"Generated payroll for {month}/{year}. "
                    f"Created {created_count}, skipped {skipped_count} existing records."
                ),
                old_values={},
                new_values={
                    "month": month,
                    "year": year,
                    "created_count": created_count,
                    "skipped_count": skipped_count,
                    "created_records": created_records,
                },
            )

            messages.success(
                request,
                f"Payroll generated successfully. Created {created_count}, skipped {skipped_count} existing records."
            )

            return redirect("payroll_record_list")

        messages.error(request, "Please correct the payroll generation form.")
    else:
        form = PayrollGenerateForm()

    return render(request, "payroll/simple_form.html", {
        "form": form,
        "title": "Generate Payroll",
        "button_text": "Generate Payroll",
        "back_url": "payroll_record_list",
    })