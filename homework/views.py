from django.contrib import messages
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import permission_required

from academics.models import ClassLevel, Stream, Subject
from students.models import Student

from audit.utils import log_audit, model_to_dict_safe

from .forms import HomeworkForm, HomeworkSubmissionForm
from .models import Homework, HomeworkSubmission


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


@permission_required("homework.view")
def homework_home(request):
    total_homework = Homework.objects.count()
    published_homework = Homework.objects.filter(status="published").count()
    closed_homework = Homework.objects.filter(status="closed").count()
    total_submissions = HomeworkSubmission.objects.count()

    recent_homework = Homework.objects.select_related(
        "class_level",
        "stream",
        "subject",
        "teacher",
    ).order_by("-created_at")[:8]

    recent_submissions = HomeworkSubmission.objects.select_related(
        "homework",
        "student",
    ).order_by("-updated_at")[:8]

    context = {
        "total_homework": total_homework,
        "published_homework": published_homework,
        "closed_homework": closed_homework,
        "total_submissions": total_submissions,
        "recent_homework": recent_homework,
        "recent_submissions": recent_submissions,
    }

    return render(request, "homework/home.html", context)


@permission_required("homework.view")
def homework_list(request):
    query = request.GET.get("q", "").strip()
    class_filter = request.GET.get("class", "").strip()
    stream_filter = request.GET.get("stream", "").strip()
    subject_filter = request.GET.get("subject", "").strip()
    status_filter = request.GET.get("status", "").strip()

    homeworks = Homework.objects.select_related(
        "academic_year",
        "term",
        "class_level",
        "stream",
        "subject",
        "teacher",
    ).all()

    if query:
        homeworks = homeworks.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(subject__name__icontains=query) |
            Q(teacher__first_name__icontains=query) |
            Q(teacher__last_name__icontains=query)
        )

    if class_filter:
        homeworks = homeworks.filter(class_level_id=class_filter)

    if stream_filter:
        homeworks = homeworks.filter(stream_id=stream_filter)

    if subject_filter:
        homeworks = homeworks.filter(subject_id=subject_filter)

    if status_filter:
        homeworks = homeworks.filter(status=status_filter)

    context = {
        "homeworks": homeworks,
        "query": query,
        "class_filter": class_filter,
        "stream_filter": stream_filter,
        "subject_filter": subject_filter,
        "status_filter": status_filter,
        "classes": ClassLevel.objects.filter(is_active=True),
        "streams": Stream.objects.filter(is_active=True),
        "subjects": Subject.objects.filter(is_active=True),
        "status_choices": Homework.STATUS_CHOICES,
    }

    return render(request, "homework/homework_list.html", context)


@permission_required("homework.manage")
def homework_create(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST, request.FILES)

        if form.is_valid():
            homework = form.save()

            log_audit(
                request,
                "create",
                obj=homework,
                message=f"Created homework: {homework}",
                new_values=model_to_dict_safe(homework),
            )

            messages.success(request, "Homework created successfully.")
            return redirect("homework_detail", pk=homework.pk)

        messages.error(request, "Please correct the homework form.")

    else:
        form = HomeworkForm(initial={
            "assigned_date": timezone.now().date(),
            "status": "published",
            "is_active": True,
        })

    return render(request, "homework/homework_form.html", {
        "form": form,
        "title": "Create Homework",
        "button_text": "Save Homework",
        "is_update": False,
    })


@permission_required("homework.manage")
def homework_update(request, pk):
    homework = get_object_or_404(Homework, pk=pk)
    old_values = model_to_dict_safe(homework)

    if request.method == "POST":
        form = HomeworkForm(request.POST, request.FILES, instance=homework)

        if form.is_valid():
            updated_homework = form.save()

            log_audit(
                request,
                "update",
                obj=updated_homework,
                message=f"Updated homework: {updated_homework}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_homework),
            )

            messages.success(request, "Homework updated successfully.")
            return redirect("homework_detail", pk=updated_homework.pk)

        messages.error(request, "Please correct the homework form.")

    else:
        form = HomeworkForm(instance=homework)

    return render(request, "homework/homework_form.html", {
        "form": form,
        "homework": homework,
        "title": "Update Homework",
        "button_text": "Update Homework",
        "is_update": True,
    })


@permission_required("homework.manage")
def homework_delete(request, pk):
    homework = get_object_or_404(Homework, pk=pk)

    if request.method == "POST":
        return safe_delete_object(
            request,
            homework,
            "Homework deleted successfully.",
            "homework_list"
        )

    return redirect("homework_list")


@permission_required("homework.view")
def homework_detail(request, pk):
    homework = get_object_or_404(
        Homework.objects.select_related(
            "academic_year",
            "term",
            "class_level",
            "stream",
            "subject",
            "teacher",
        ),
        pk=pk
    )

    submissions = HomeworkSubmission.objects.select_related(
        "student",
        "student__class_level",
        "student__stream",
    ).filter(homework=homework)

    total_students_qs = Student.objects.filter(
        class_level=homework.class_level,
        status="active"
    )

    if homework.stream:
        total_students_qs = total_students_qs.filter(stream=homework.stream)

    total_students = total_students_qs.count()
    submitted_count = submissions.exclude(status="not_submitted").count()
    not_submitted_count = total_students - submitted_count

    context = {
        "homework": homework,
        "submissions": submissions,
        "total_students": total_students,
        "submitted_count": submitted_count,
        "not_submitted_count": not_submitted_count,
    }

    return render(request, "homework/homework_detail.html", context)


@permission_required("homework.view")
def submission_list(request):
    query = request.GET.get("q", "").strip()
    homework_filter = request.GET.get("homework", "").strip()
    status_filter = request.GET.get("status", "").strip()

    submissions = HomeworkSubmission.objects.select_related(
        "homework",
        "student",
        "student__class_level",
        "student__stream",
    ).all()

    if query:
        submissions = submissions.filter(
            Q(student__admission_number__icontains=query) |
            Q(student__first_name__icontains=query) |
            Q(student__middle_name__icontains=query) |
            Q(student__last_name__icontains=query) |
            Q(homework__title__icontains=query)
        )

    if homework_filter:
        submissions = submissions.filter(homework_id=homework_filter)

    if status_filter:
        submissions = submissions.filter(status=status_filter)

    context = {
        "submissions": submissions,
        "query": query,
        "homework_filter": homework_filter,
        "status_filter": status_filter,
        "homeworks": Homework.objects.filter(is_active=True),
        "status_choices": HomeworkSubmission.STATUS_CHOICES,
    }

    return render(request, "homework/submission_list.html", context)


@permission_required("homework.manage")
def submission_create(request):
    if request.method == "POST":
        form = HomeworkSubmissionForm(request.POST, request.FILES)

        if form.is_valid():
            submission = form.save()

            log_audit(
                request,
                "create",
                obj=submission,
                message=f"Created homework submission: {submission}",
                new_values=model_to_dict_safe(submission),
            )

            messages.success(request, "Homework submission saved successfully.")
            return redirect("homework_detail", pk=submission.homework.pk)

        messages.error(request, "Please correct the submission form.")

    else:
        form = HomeworkSubmissionForm(initial={
            "submitted_date": timezone.now().date(),
            "status": "submitted",
        })

    return render(request, "homework/submission_form.html", {
        "form": form,
        "title": "Add Submission",
        "button_text": "Save Submission",
        "is_update": False,
    })


@permission_required("homework.manage")
def submission_update(request, pk):
    submission = get_object_or_404(
        HomeworkSubmission.objects.select_related("homework", "student"),
        pk=pk
    )
    old_values = model_to_dict_safe(submission)

    if request.method == "POST":
        form = HomeworkSubmissionForm(request.POST, request.FILES, instance=submission)

        if form.is_valid():
            updated_submission = form.save()

            log_audit(
                request,
                "update",
                obj=updated_submission,
                message=f"Updated homework submission: {updated_submission}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_submission),
            )

            messages.success(request, "Homework submission updated successfully.")
            return redirect("homework_detail", pk=updated_submission.homework.pk)

        messages.error(request, "Please correct the submission form.")

    else:
        form = HomeworkSubmissionForm(instance=submission)

    return render(request, "homework/submission_form.html", {
        "form": form,
        "submission": submission,
        "title": "Update Submission",
        "button_text": "Update Submission",
        "is_update": True,
    })


@permission_required("homework.manage")
def submission_delete(request, pk):
    submission = get_object_or_404(HomeworkSubmission, pk=pk)
    homework_id = submission.homework_id

    old_values = model_to_dict_safe(submission)
    app_label = submission._meta.app_label
    model_name = submission._meta.model_name
    object_id = str(submission.pk)
    object_repr = str(submission)

    if request.method == "POST":
        submission.delete()

        log_audit(
            request,
            "delete",
            app_label=app_label,
            model_name=model_name,
            object_id=object_id,
            object_repr=object_repr,
            message=f"Deleted homework submission: {object_repr}",
            old_values=old_values,
        )

        messages.success(request, "Homework submission deleted successfully.")
        return redirect("homework_detail", pk=homework_id)

    return redirect("homework_detail", pk=homework_id)


@permission_required("homework.manage")
def auto_create_homework_submissions(request, pk):
    homework = get_object_or_404(Homework, pk=pk)

    students = Student.objects.filter(
        class_level=homework.class_level,
        status="active"
    )

    if homework.stream:
        students = students.filter(stream=homework.stream)

    created_count = 0
    created_submission_ids = []

    for student in students:
        submission, created = HomeworkSubmission.objects.get_or_create(
            homework=homework,
            student=student,
            defaults={
                "status": "not_submitted",
            }
        )

        if created:
            created_count += 1
            created_submission_ids.append(submission.pk)

    log_audit(
        request,
        "generate",
        obj=homework,
        message=f"Auto-created homework submission records for homework: {homework}. Created {created_count} records.",
        new_values={
            "homework_id": homework.pk,
            "homework": str(homework),
            "created_count": created_count,
            "created_submission_ids": created_submission_ids,
        },
    )

    messages.success(
        request,
        f"Submission list ready. Created {created_count} student records."
    )

    return redirect("homework_detail", pk=homework.pk)