from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404

from accounts.decorators import permission_required

from audit.utils import log_audit, model_to_dict_safe

from .forms import ParentGuardianForm, StudentForm
from .models import ParentGuardian, Student


@permission_required("students.view")
def student_list(request):
    query = request.GET.get("q", "").strip()
    class_filter = request.GET.get("class", "").strip()
    status_filter = request.GET.get("status", "").strip()

    students = Student.objects.select_related(
        "class_level",
        "stream",
        "parent_guardian"
    ).all()

    if query:
        students = students.filter(
            Q(admission_number__icontains=query) |
            Q(first_name__icontains=query) |
            Q(middle_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(parent_guardian__full_name__icontains=query) |
            Q(parent_guardian__phone__icontains=query)
        )

    if class_filter:
        students = students.filter(class_level_id=class_filter)

    if status_filter:
        students = students.filter(status=status_filter)

    from academics.models import ClassLevel

    context = {
        "students": students,
        "classes": ClassLevel.objects.filter(is_active=True),
        "query": query,
        "class_filter": class_filter,
        "status_filter": status_filter,
    }

    return render(request, "students/student_list.html", context)


@permission_required("students.manage")
def student_create(request):
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)

        if form.is_valid():
            student = form.save()

            log_audit(
                request,
                "create",
                obj=student,
                message=f"Admitted new student: {student}",
                old_values={},
                new_values=model_to_dict_safe(student),
            )

            messages.success(request, "Student admitted successfully.")
            return redirect("student_list")

        messages.error(request, "Please correct the student form.")

    else:
        form = StudentForm()

    return render(request, "students/student_form.html", {
        "form": form,
        "title": "Admit Student",
    })


@permission_required("students.view")
def student_detail(request, pk):
    student = get_object_or_404(
        Student.objects.select_related(
            "class_level",
            "stream",
            "parent_guardian",
        ),
        pk=pk
    )

    return render(request, "students/student_detail.html", {
        "student": student,
    })


@permission_required("students.manage")
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    old_values = model_to_dict_safe(student)

    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES, instance=student)

        if form.is_valid():
            updated_student = form.save()

            log_audit(
                request,
                "update",
                obj=updated_student,
                message=f"Updated student: {updated_student}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_student),
            )

            messages.success(request, "Student updated successfully.")
            return redirect("student_detail", pk=updated_student.pk)

        messages.error(request, "Please correct the student form.")

    else:
        form = StudentForm(instance=student)

    return render(request, "students/student_form.html", {
        "form": form,
        "title": "Update Student",
    })


@permission_required("parents.view")
def parent_list(request):
    query = request.GET.get("q", "").strip()

    parents = ParentGuardian.objects.select_related("user").all()

    if query:
        parents = parents.filter(
            Q(full_name__icontains=query) |
            Q(phone__icontains=query) |
            Q(alternative_phone__icontains=query) |
            Q(email__icontains=query)
        )

    return render(request, "students/parent_list.html", {
        "parents": parents,
        "query": query,
    })


@permission_required("parents.manage")
def parent_create(request):
    if request.method == "POST":
        form = ParentGuardianForm(request.POST)

        if form.is_valid():
            parent = form.save()

            log_audit(
                request,
                "create",
                obj=parent,
                message=f"Created parent / guardian: {parent}",
                old_values={},
                new_values=model_to_dict_safe(parent),
            )

            messages.success(request, "Parent / guardian added successfully.")
            return redirect("parent_list")

        messages.error(request, "Please correct the parent form.")

    else:
        form = ParentGuardianForm()

    return render(request, "students/parent_form.html", {
        "form": form,
        "title": "Add Parent / Guardian",
    })


@permission_required("parents.manage")
def parent_update(request, pk):
    parent = get_object_or_404(ParentGuardian, pk=pk)
    old_values = model_to_dict_safe(parent)

    if request.method == "POST":
        form = ParentGuardianForm(request.POST, instance=parent)

        if form.is_valid():
            updated_parent = form.save()

            log_audit(
                request,
                "update",
                obj=updated_parent,
                message=f"Updated parent / guardian: {updated_parent}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_parent),
            )

            messages.success(request, "Parent / guardian updated successfully.")
            return redirect("parent_list")

        messages.error(request, "Please correct the parent form.")

    else:
        form = ParentGuardianForm(instance=parent)

    return render(request, "students/parent_form.html", {
        "form": form,
        "title": "Update Parent / Guardian",
        "parent": parent,
    })


@permission_required("admissions.view")
def admission_list(request):
    query = request.GET.get("q", "").strip()
    class_filter = request.GET.get("class", "").strip()
    boarding_filter = request.GET.get("boarding", "").strip()
    status_filter = request.GET.get("status", "").strip()

    admissions = Student.objects.select_related(
        "class_level",
        "stream",
        "parent_guardian"
    ).all()

    if query:
        admissions = admissions.filter(
            Q(admission_number__icontains=query) |
            Q(first_name__icontains=query) |
            Q(middle_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(parent_guardian__full_name__icontains=query) |
            Q(parent_guardian__phone__icontains=query)
        )

    if class_filter:
        admissions = admissions.filter(class_level_id=class_filter)

    if boarding_filter:
        admissions = admissions.filter(boarding_status=boarding_filter)

    if status_filter:
        admissions = admissions.filter(status=status_filter)

    from academics.models import ClassLevel

    context = {
        "admissions": admissions,
        "classes": ClassLevel.objects.filter(is_active=True),
        "query": query,
        "class_filter": class_filter,
        "boarding_filter": boarding_filter,
        "status_filter": status_filter,
        "boarding_choices": Student.BOARDING_CHOICES,
        "status_choices": Student.STATUS_CHOICES,
    }

    return render(request, "students/admission_list.html", context)