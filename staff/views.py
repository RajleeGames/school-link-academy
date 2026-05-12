from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import permission_required

from audit.utils import log_audit, model_to_dict_safe

from .forms import StaffProfileForm
from .models import StaffProfile


@permission_required("staff.view")
def staff_list(request):
    query = request.GET.get("q", "").strip()
    role_filter = request.GET.get("role", "").strip()
    status_filter = request.GET.get("status", "").strip()

    staff_members = StaffProfile.objects.prefetch_related(
        "assigned_classes",
        "subjects"
    ).all()

    if query:
        staff_members = staff_members.filter(
            Q(staff_id__icontains=query) |
            Q(first_name__icontains=query) |
            Q(middle_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query)
        )

    if role_filter:
        staff_members = staff_members.filter(role=role_filter)

    if status_filter:
        staff_members = staff_members.filter(status=status_filter)

    context = {
        "staff_members": staff_members,
        "query": query,
        "role_filter": role_filter,
        "status_filter": status_filter,
        "role_choices": StaffProfile.ROLE_CHOICES,
        "status_choices": StaffProfile.STATUS_CHOICES,
    }

    return render(request, "staff/staff_list.html", context)


@permission_required("staff.manage")
def staff_create(request):
    if request.method == "POST":
        form = StaffProfileForm(request.POST, request.FILES)

        if form.is_valid():
            staff = form.save()

            log_audit(
                request,
                "create",
                obj=staff,
                message=f"Created staff member: {staff}",
                old_values={},
                new_values=model_to_dict_safe(staff),
            )

            messages.success(request, "Staff member added successfully.")
            return redirect("staff_detail", pk=staff.pk)

        messages.error(request, "Please correct the staff form.")

    else:
        form = StaffProfileForm()

    return render(request, "staff/staff_form.html", {
        "form": form,
        "title": "Add Staff Member",
    })


@permission_required("staff.view")
def staff_detail(request, pk):
    staff = get_object_or_404(
        StaffProfile.objects.prefetch_related("assigned_classes", "subjects"),
        pk=pk
    )

    return render(request, "staff/staff_detail.html", {
        "staff": staff,
    })


@permission_required("staff.manage")
def staff_update(request, pk):
    staff = get_object_or_404(StaffProfile, pk=pk)
    old_values = model_to_dict_safe(staff)

    if request.method == "POST":
        form = StaffProfileForm(request.POST, request.FILES, instance=staff)

        if form.is_valid():
            updated_staff = form.save()

            log_audit(
                request,
                "update",
                obj=updated_staff,
                message=f"Updated staff member: {updated_staff}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_staff),
            )

            messages.success(request, "Staff member updated successfully.")
            return redirect("staff_detail", pk=updated_staff.pk)

        messages.error(request, "Please correct the staff form.")

    else:
        form = StaffProfileForm(instance=staff)

    return render(request, "staff/staff_form.html", {
        "form": form,
        "title": "Update Staff Member",
    })