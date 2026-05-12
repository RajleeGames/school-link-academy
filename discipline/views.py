from django.contrib import messages
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import permission_required

from academics.models import ClassLevel, Stream

from audit.utils import log_audit, model_to_dict_safe

from .forms import DisciplineCategoryForm, DisciplineRecordForm, DisciplineFollowUpForm
from .models import DisciplineCategory, DisciplineRecord, DisciplineFollowUp


def safe_delete_object(request, obj, success_message, redirect_url):
    old_values = model_to_dict_safe(obj)
    app_label = obj._meta.app_label
    model_name = obj._meta.model_name
    object_id = str(obj.pk)
    object_repr = str(obj)

    try:
        obj.delete()

        log_audit(
            request,
            "delete",
            app_label=app_label,
            model_name=model_name,
            object_id=object_id,
            object_repr=object_repr,
            message=f"Deleted {model_name}: {object_repr}",
            old_values=old_values,
            new_values={},
        )

        messages.success(request, success_message)

    except ProtectedError:
        messages.error(
            request,
            "This record cannot be deleted because it is already used somewhere. You can edit it or mark it inactive instead."
        )

    except Exception:
        messages.error(
            request,
            "This record could not be deleted. Please check if it is connected to other records."
        )

    return redirect(redirect_url)


@permission_required("discipline.view")
def discipline_home(request):
    total_records = DisciplineRecord.objects.count()
    open_records = DisciplineRecord.objects.filter(status="open").count()
    resolved_records = DisciplineRecord.objects.filter(status="resolved").count()
    reward_records = DisciplineRecord.objects.filter(record_type="reward").count()

    recent_records = DisciplineRecord.objects.select_related(
        "student",
        "student__class_level",
        "student__stream",
        "category",
        "reported_by",
    ).order_by("-created_at")[:8]

    recent_followups = DisciplineFollowUp.objects.select_related(
        "record",
        "record__student",
        "handled_by",
    ).order_by("-created_at")[:8]

    context = {
        "total_records": total_records,
        "open_records": open_records,
        "resolved_records": resolved_records,
        "reward_records": reward_records,
        "recent_records": recent_records,
        "recent_followups": recent_followups,
    }

    return render(request, "discipline/home.html", context)


@permission_required("discipline.manage")
def discipline_category_list(request):
    categories = DisciplineCategory.objects.all()

    if request.method == "POST":
        form = DisciplineCategoryForm(request.POST)

        if form.is_valid():
            category = form.save()

            log_audit(
                request,
                "create",
                obj=category,
                message=f"Created discipline category: {category}",
                old_values={},
                new_values=model_to_dict_safe(category),
            )

            messages.success(request, "Discipline category saved successfully.")
            return redirect("discipline_category_list")

        messages.error(request, "Please correct the category form.")

    else:
        form = DisciplineCategoryForm()

    return render(request, "discipline/category_list.html", {
        "categories": categories,
        "form": form,
    })


@permission_required("discipline.manage")
def discipline_category_update(request, pk):
    category = get_object_or_404(DisciplineCategory, pk=pk)
    old_values = model_to_dict_safe(category)

    if request.method == "POST":
        form = DisciplineCategoryForm(request.POST, instance=category)

        if form.is_valid():
            updated_category = form.save()

            log_audit(
                request,
                "update",
                obj=updated_category,
                message=f"Updated discipline category: {updated_category}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_category),
            )

            messages.success(request, "Discipline category updated successfully.")
            return redirect("discipline_category_list")

        messages.error(request, "Please correct the category form.")

    else:
        form = DisciplineCategoryForm(instance=category)

    return render(request, "discipline/simple_discipline_form.html", {
        "form": form,
        "title": "Update Discipline Category",
        "button_text": "Update Category",
        "back_url": "discipline_category_list",
    })


@permission_required("discipline.manage")
def discipline_category_delete(request, pk):
    category = get_object_or_404(DisciplineCategory, pk=pk)

    if request.method == "POST":
        return safe_delete_object(
            request,
            category,
            "Discipline category deleted successfully.",
            "discipline_category_list"
        )

    return redirect("discipline_category_list")


@permission_required("discipline.view")
def discipline_record_list(request):
    query = request.GET.get("q", "").strip()
    class_filter = request.GET.get("class", "").strip()
    stream_filter = request.GET.get("stream", "").strip()
    type_filter = request.GET.get("type", "").strip()
    severity_filter = request.GET.get("severity", "").strip()
    status_filter = request.GET.get("status", "").strip()

    records = DisciplineRecord.objects.select_related(
        "student",
        "student__class_level",
        "student__stream",
        "category",
        "reported_by",
    ).all()

    if query:
        records = records.filter(
            Q(student__admission_number__icontains=query) |
            Q(student__first_name__icontains=query) |
            Q(student__middle_name__icontains=query) |
            Q(student__last_name__icontains=query) |
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(action_taken__icontains=query)
        )

    if class_filter:
        records = records.filter(student__class_level_id=class_filter)

    if stream_filter:
        records = records.filter(student__stream_id=stream_filter)

    if type_filter:
        records = records.filter(record_type=type_filter)

    if severity_filter:
        records = records.filter(severity=severity_filter)

    if status_filter:
        records = records.filter(status=status_filter)

    context = {
        "records": records,
        "query": query,
        "class_filter": class_filter,
        "stream_filter": stream_filter,
        "type_filter": type_filter,
        "severity_filter": severity_filter,
        "status_filter": status_filter,
        "classes": ClassLevel.objects.filter(is_active=True),
        "streams": Stream.objects.filter(is_active=True),
        "record_type_choices": DisciplineRecord.RECORD_TYPE_CHOICES,
        "severity_choices": DisciplineRecord.SEVERITY_CHOICES,
        "status_choices": DisciplineRecord.STATUS_CHOICES,
    }

    return render(request, "discipline/record_list.html", context)


@permission_required("discipline.manage")
def discipline_record_create(request):
    if request.method == "POST":
        form = DisciplineRecordForm(request.POST, request.FILES)

        if form.is_valid():
            record = form.save()

            log_audit(
                request,
                "create",
                obj=record,
                message=f"Created discipline record: {record}",
                old_values={},
                new_values=model_to_dict_safe(record),
            )

            messages.success(request, "Discipline record saved successfully.")
            return redirect("discipline_record_detail", pk=record.pk)

        messages.error(request, "Please correct the discipline form.")

    else:
        form = DisciplineRecordForm(initial={
            "incident_date": timezone.now().date(),
            "status": "open",
        })

    return render(request, "discipline/record_form.html", {
        "form": form,
        "title": "Add Discipline Record",
        "button_text": "Save Record",
        "is_update": False,
    })


@permission_required("discipline.manage")
def discipline_record_update(request, pk):
    record = get_object_or_404(DisciplineRecord, pk=pk)
    old_values = model_to_dict_safe(record)

    if request.method == "POST":
        form = DisciplineRecordForm(request.POST, request.FILES, instance=record)

        if form.is_valid():
            updated_record = form.save()

            log_audit(
                request,
                "update",
                obj=updated_record,
                message=f"Updated discipline record: {updated_record}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_record),
            )

            messages.success(request, "Discipline record updated successfully.")
            return redirect("discipline_record_detail", pk=updated_record.pk)

        messages.error(request, "Please correct the discipline form.")

    else:
        form = DisciplineRecordForm(instance=record)

    return render(request, "discipline/record_form.html", {
        "form": form,
        "record": record,
        "title": "Update Discipline Record",
        "button_text": "Update Record",
        "is_update": True,
    })


@permission_required("discipline.manage")
def discipline_record_delete(request, pk):
    record = get_object_or_404(DisciplineRecord, pk=pk)

    if request.method == "POST":
        return safe_delete_object(
            request,
            record,
            "Discipline record deleted successfully.",
            "discipline_record_list"
        )

    return redirect("discipline_record_list")


@permission_required("discipline.view")
def discipline_record_detail(request, pk):
    record = get_object_or_404(
        DisciplineRecord.objects.select_related(
            "student",
            "student__class_level",
            "student__stream",
            "student__parent_guardian",
            "category",
            "reported_by",
        ),
        pk=pk
    )

    followups = record.followups.select_related("handled_by").all()

    return render(request, "discipline/record_detail.html", {
        "record": record,
        "followups": followups,
    })


@permission_required("discipline.view")
def followup_list(request):
    query = request.GET.get("q", "").strip()

    followups = DisciplineFollowUp.objects.select_related(
        "record",
        "record__student",
        "handled_by",
    ).all()

    if query:
        followups = followups.filter(
            Q(record__title__icontains=query) |
            Q(record__student__admission_number__icontains=query) |
            Q(record__student__first_name__icontains=query) |
            Q(record__student__last_name__icontains=query) |
            Q(note__icontains=query) |
            Q(next_action__icontains=query)
        )

    context = {
        "followups": followups,
        "query": query,
    }

    return render(request, "discipline/followup_list.html", context)


@permission_required("discipline.manage")
def followup_create(request):
    record_id = request.GET.get("record", "")

    initial = {
        "follow_up_date": timezone.now().date(),
    }

    if record_id:
        initial["record"] = record_id

    if request.method == "POST":
        form = DisciplineFollowUpForm(request.POST)

        if form.is_valid():
            followup = form.save()

            log_audit(
                request,
                "create",
                obj=followup,
                message=f"Created discipline follow-up: {followup}",
                old_values={},
                new_values=model_to_dict_safe(followup),
            )

            messages.success(request, "Follow-up saved successfully.")
            return redirect("discipline_record_detail", pk=followup.record.pk)

        messages.error(request, "Please correct the follow-up form.")

    else:
        form = DisciplineFollowUpForm(initial=initial)

    return render(request, "discipline/followup_form.html", {
        "form": form,
        "title": "Add Follow Up",
        "button_text": "Save Follow Up",
        "is_update": False,
    })


@permission_required("discipline.manage")
def followup_update(request, pk):
    followup = get_object_or_404(
        DisciplineFollowUp.objects.select_related("record"),
        pk=pk
    )
    old_values = model_to_dict_safe(followup)

    if request.method == "POST":
        form = DisciplineFollowUpForm(request.POST, instance=followup)

        if form.is_valid():
            updated_followup = form.save()

            log_audit(
                request,
                "update",
                obj=updated_followup,
                message=f"Updated discipline follow-up: {updated_followup}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_followup),
            )

            messages.success(request, "Follow-up updated successfully.")
            return redirect("discipline_record_detail", pk=updated_followup.record.pk)

        messages.error(request, "Please correct the follow-up form.")

    else:
        form = DisciplineFollowUpForm(instance=followup)

    return render(request, "discipline/followup_form.html", {
        "form": form,
        "followup": followup,
        "title": "Update Follow Up",
        "button_text": "Update Follow Up",
        "is_update": True,
    })


@permission_required("discipline.manage")
def followup_delete(request, pk):
    followup = get_object_or_404(DisciplineFollowUp, pk=pk)
    record_id = followup.record_id

    old_values = model_to_dict_safe(followup)
    app_label = followup._meta.app_label
    model_name = followup._meta.model_name
    object_id = str(followup.pk)
    object_repr = str(followup)

    if request.method == "POST":
        followup.delete()

        log_audit(
            request,
            "delete",
            app_label=app_label,
            model_name=model_name,
            object_id=object_id,
            object_repr=object_repr,
            message=f"Deleted discipline follow-up: {object_repr}",
            old_values=old_values,
            new_values={},
        )

        messages.success(request, "Follow-up deleted successfully.")
        return redirect("discipline_record_detail", pk=record_id)

    return redirect("discipline_record_detail", pk=record_id)