from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import permission_required

from audit.utils import log_audit, model_to_dict_safe

from .forms import AcademicYearForm, TermForm, ClassLevelForm, StreamForm, SubjectForm
from .models import AcademicYear, Term, ClassLevel, Stream, Subject


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


@permission_required("academics.view")
def academics_home(request):
    context = {
        "academic_years_count": AcademicYear.objects.count(),
        "terms_count": Term.objects.count(),
        "classes_count": ClassLevel.objects.count(),
        "streams_count": Stream.objects.count(),
        "subjects_count": Subject.objects.count(),
        "current_year": AcademicYear.objects.filter(is_current=True).first(),
        "current_term": Term.objects.select_related("academic_year").filter(is_current=True).first(),
    }
    return render(request, "academics/home.html", context)


@permission_required("academics.view")
def academic_year_list(request):
    context = {
        "academic_years": AcademicYear.objects.all(),
        "form": AcademicYearForm(),
    }
    return render(request, "academics/academic_year_list.html", context)


@permission_required("academics.view")
def term_list(request):
    context = {
        "terms": Term.objects.select_related("academic_year").all(),
        "form": TermForm(),
    }
    return render(request, "academics/term_list.html", context)


@permission_required("academics.view")
def class_level_list(request):
    context = {
        "classes": ClassLevel.objects.all(),
        "form": ClassLevelForm(),
    }
    return render(request, "academics/class_level_list.html", context)


@permission_required("academics.view")
def stream_list(request):
    context = {
        "streams": Stream.objects.select_related("class_level").all(),
        "form": StreamForm(),
    }
    return render(request, "academics/stream_list.html", context)


@permission_required("subjects.view")
def subject_list(request):
    context = {
        "subjects": Subject.objects.prefetch_related("class_levels").all(),
        "form": SubjectForm(),
    }
    return render(request, "academics/subject_list.html", context)


@permission_required("academics.manage")
def academic_year_create(request):
    if request.method == "POST":
        form = AcademicYearForm(request.POST)

        if form.is_valid():
            if form.cleaned_data.get("is_current"):
                old_current_years = list(AcademicYear.objects.filter(is_current=True))

                AcademicYear.objects.update(is_current=False)

                for old_year in old_current_years:
                    old_values = model_to_dict_safe(old_year)
                    old_year.refresh_from_db()

                    log_audit(
                        request,
                        "update",
                        obj=old_year,
                        message=f"Unset previous current academic year: {old_year}",
                        old_values=old_values,
                        new_values=model_to_dict_safe(old_year),
                    )

            academic_year = form.save()

            log_audit(
                request,
                "create",
                obj=academic_year,
                message=f"Created academic year: {academic_year}",
                old_values={},
                new_values=model_to_dict_safe(academic_year),
            )

            messages.success(request, "Academic year added successfully.")
        else:
            messages.error(request, "Please correct the academic year form.")

    return redirect("academic_year_list")


@permission_required("academics.manage")
def term_create(request):
    if request.method == "POST":
        form = TermForm(request.POST)

        if form.is_valid():
            if form.cleaned_data.get("is_current"):
                old_current_terms = list(Term.objects.filter(is_current=True))

                Term.objects.update(is_current=False)

                for old_term in old_current_terms:
                    old_values = model_to_dict_safe(old_term)
                    old_term.refresh_from_db()

                    log_audit(
                        request,
                        "update",
                        obj=old_term,
                        message=f"Unset previous current term: {old_term}",
                        old_values=old_values,
                        new_values=model_to_dict_safe(old_term),
                    )

            term = form.save()

            log_audit(
                request,
                "create",
                obj=term,
                message=f"Created academic term: {term}",
                old_values={},
                new_values=model_to_dict_safe(term),
            )

            messages.success(request, "Term added successfully.")
        else:
            messages.error(request, "Please correct the term form.")

    return redirect("term_list")


@permission_required("academics.manage")
def class_level_create(request):
    if request.method == "POST":
        form = ClassLevelForm(request.POST)

        if form.is_valid():
            class_level = form.save()

            log_audit(
                request,
                "create",
                obj=class_level,
                message=f"Created class level: {class_level}",
                old_values={},
                new_values=model_to_dict_safe(class_level),
            )

            messages.success(request, "Class level added successfully.")
        else:
            messages.error(request, "Please correct the class form.")

    return redirect("class_level_list")


@permission_required("academics.manage")
def stream_create(request):
    if request.method == "POST":
        form = StreamForm(request.POST)

        if form.is_valid():
            stream = form.save()

            log_audit(
                request,
                "create",
                obj=stream,
                message=f"Created stream: {stream}",
                old_values={},
                new_values=model_to_dict_safe(stream),
            )

            messages.success(request, "Stream added successfully.")
        else:
            messages.error(request, "Please correct the stream form.")

    return redirect("stream_list")


@permission_required("subjects.manage")
def subject_create(request):
    if request.method == "POST":
        form = SubjectForm(request.POST)

        if form.is_valid():
            subject = form.save()

            log_audit(
                request,
                "create",
                obj=subject,
                message=f"Created subject: {subject}",
                old_values={},
                new_values=model_to_dict_safe(subject),
            )

            messages.success(request, "Subject added successfully.")
        else:
            messages.error(request, "Please correct the subject form.")

    return redirect("subject_list")


@permission_required("academics.manage")
def academic_year_update(request, pk):
    academic_year = get_object_or_404(AcademicYear, pk=pk)

    if request.method == "POST":
        old_values = model_to_dict_safe(academic_year)
        form = AcademicYearForm(request.POST, instance=academic_year)

        if form.is_valid():
            if form.cleaned_data.get("is_current"):
                old_current_years = list(
                    AcademicYear.objects.filter(is_current=True).exclude(pk=academic_year.pk)
                )

                AcademicYear.objects.exclude(pk=academic_year.pk).update(is_current=False)

                for old_year in old_current_years:
                    old_year_values = model_to_dict_safe(old_year)
                    old_year.refresh_from_db()

                    log_audit(
                        request,
                        "update",
                        obj=old_year,
                        message=f"Unset previous current academic year: {old_year}",
                        old_values=old_year_values,
                        new_values=model_to_dict_safe(old_year),
                    )

            updated_year = form.save()

            log_audit(
                request,
                "update",
                obj=updated_year,
                message=f"Updated academic year: {updated_year}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_year),
            )

            messages.success(request, "Academic year updated successfully.")
            return redirect("academic_year_list")

        messages.error(request, "Please correct the academic year form.")
    else:
        form = AcademicYearForm(instance=academic_year)

    return render(request, "academics/academic_form.html", {
        "form": form,
        "title": "Update Academic Year",
        "back_url": "academic_year_list",
        "button_text": "Update Academic Year",
    })


@permission_required("academics.manage")
def term_update(request, pk):
    term = get_object_or_404(Term, pk=pk)

    if request.method == "POST":
        old_values = model_to_dict_safe(term)
        form = TermForm(request.POST, instance=term)

        if form.is_valid():
            if form.cleaned_data.get("is_current"):
                old_current_terms = list(
                    Term.objects.filter(is_current=True).exclude(pk=term.pk)
                )

                Term.objects.exclude(pk=term.pk).update(is_current=False)

                for old_term in old_current_terms:
                    old_term_values = model_to_dict_safe(old_term)
                    old_term.refresh_from_db()

                    log_audit(
                        request,
                        "update",
                        obj=old_term,
                        message=f"Unset previous current term: {old_term}",
                        old_values=old_term_values,
                        new_values=model_to_dict_safe(old_term),
                    )

            updated_term = form.save()

            log_audit(
                request,
                "update",
                obj=updated_term,
                message=f"Updated academic term: {updated_term}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_term),
            )

            messages.success(request, "Term updated successfully.")
            return redirect("term_list")

        messages.error(request, "Please correct the term form.")
    else:
        form = TermForm(instance=term)

    return render(request, "academics/academic_form.html", {
        "form": form,
        "title": "Update Term",
        "back_url": "term_list",
        "button_text": "Update Term",
    })


@permission_required("academics.manage")
def class_level_update(request, pk):
    class_level = get_object_or_404(ClassLevel, pk=pk)

    if request.method == "POST":
        old_values = model_to_dict_safe(class_level)
        form = ClassLevelForm(request.POST, instance=class_level)

        if form.is_valid():
            updated_class_level = form.save()

            log_audit(
                request,
                "update",
                obj=updated_class_level,
                message=f"Updated class level: {updated_class_level}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_class_level),
            )

            messages.success(request, "Class level updated successfully.")
            return redirect("class_level_list")

        messages.error(request, "Please correct the class form.")
    else:
        form = ClassLevelForm(instance=class_level)

    return render(request, "academics/academic_form.html", {
        "form": form,
        "title": "Update Class",
        "back_url": "class_level_list",
        "button_text": "Update Class",
    })


@permission_required("academics.manage")
def stream_update(request, pk):
    stream = get_object_or_404(Stream, pk=pk)

    if request.method == "POST":
        old_values = model_to_dict_safe(stream)
        form = StreamForm(request.POST, instance=stream)

        if form.is_valid():
            updated_stream = form.save()

            log_audit(
                request,
                "update",
                obj=updated_stream,
                message=f"Updated stream: {updated_stream}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_stream),
            )

            messages.success(request, "Stream updated successfully.")
            return redirect("stream_list")

        messages.error(request, "Please correct the stream form.")
    else:
        form = StreamForm(instance=stream)

    return render(request, "academics/academic_form.html", {
        "form": form,
        "title": "Update Stream",
        "back_url": "stream_list",
        "button_text": "Update Stream",
    })


@permission_required("subjects.manage")
def subject_update(request, pk):
    subject = get_object_or_404(Subject, pk=pk)

    if request.method == "POST":
        old_values = model_to_dict_safe(subject)
        form = SubjectForm(request.POST, instance=subject)

        if form.is_valid():
            updated_subject = form.save()

            log_audit(
                request,
                "update",
                obj=updated_subject,
                message=f"Updated subject: {updated_subject}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_subject),
            )

            messages.success(request, "Subject updated successfully.")
            return redirect("subject_list")

        messages.error(request, "Please correct the subject form.")
    else:
        form = SubjectForm(instance=subject)

    return render(request, "academics/academic_form.html", {
        "form": form,
        "title": "Update Subject",
        "back_url": "subject_list",
        "button_text": "Update Subject",
    })


@permission_required("academics.manage")
def academic_year_delete(request, pk):
    academic_year = get_object_or_404(AcademicYear, pk=pk)

    if request.method == "POST":
        return safe_delete_object(
            request,
            academic_year,
            "Academic year deleted successfully.",
            "academic_year_list"
        )

    return redirect("academic_year_list")


@permission_required("academics.manage")
def term_delete(request, pk):
    term = get_object_or_404(Term, pk=pk)

    if request.method == "POST":
        return safe_delete_object(
            request,
            term,
            "Term deleted successfully.",
            "term_list"
        )

    return redirect("term_list")


@permission_required("academics.manage")
def class_level_delete(request, pk):
    class_level = get_object_or_404(ClassLevel, pk=pk)

    if request.method == "POST":
        return safe_delete_object(
            request,
            class_level,
            "Class deleted successfully.",
            "class_level_list"
        )

    return redirect("class_level_list")


@permission_required("academics.manage")
def stream_delete(request, pk):
    stream = get_object_or_404(Stream, pk=pk)

    if request.method == "POST":
        return safe_delete_object(
            request,
            stream,
            "Stream deleted successfully.",
            "stream_list"
        )

    return redirect("stream_list")


@permission_required("subjects.manage")
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)

    if request.method == "POST":
        return safe_delete_object(
            request,
            subject,
            "Subject deleted successfully.",
            "subject_list"
        )

    return redirect("subject_list")