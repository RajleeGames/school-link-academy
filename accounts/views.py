from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from attendance.models import StudentAttendance
from exams.models import ExamResult
from fees.models import FeePayment, StudentInvoice
from students.models import ParentGuardian
from django.db.models import Count, Q, Sum
from accounts.decorators import permission_required
from accounts.permissions import user_has_permission
from decimal import Decimal
from audit.utils import log_audit, model_to_dict_safe
from fees.utils import build_invoice_fee_breakdown, sync_invoice_items_from_fee_structure
from .forms import (
    AdminUserPasswordResetForm,
    CreateParentLoginForm,
    SchoolLoginForm,
    UserProfileRoleForm,
)
from .models import UserProfile


def user_safe_values(user_obj):
    if not user_obj:
        return {}

    profile = getattr(user_obj, "account_profile", None)

    data = {
        "id": str(user_obj.pk),
        "username": user_obj.username,
        "email": user_obj.email,
        "first_name": user_obj.first_name,
        "last_name": user_obj.last_name,
        "is_active": str(user_obj.is_active),
        "is_staff": str(user_obj.is_staff),
        "is_superuser": str(user_obj.is_superuser),
        "last_login": str(user_obj.last_login) if user_obj.last_login else "",
        "date_joined": str(user_obj.date_joined) if user_obj.date_joined else "",
    }

    if profile:
        data.update({
            "profile_id": str(profile.pk),
            "role": profile.role,
            "phone": profile.phone,
            "is_active_profile": str(profile.is_active_profile),
        })

    return data


def get_role_redirect(user):
    if user.is_superuser:
        return "dashboard"

    profile = getattr(user, "account_profile", None)

    if not profile:
        return "dashboard"

    if not profile.is_active_profile:
        return "login"

    if profile.role == "parent":
        return "parent_portal_home"

    return "dashboard"


class SchoolLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = SchoolLoginForm

    def form_valid(self, form):
        user = form.get_user()
        profile = getattr(user, "account_profile", None)

        if profile and not profile.is_active_profile:
            log_audit(
                self.request,
                "login",
                app_label="auth",
                model_name="user",
                object_id=str(user.pk),
                object_repr=user.username,
                message=f"Blocked login attempt for inactive account: {user.username}",
                old_values={},
                new_values=user_safe_values(user),
            )

            messages.error(
                self.request,
                "Your account is inactive. Contact administrator."
            )
            return redirect("login")

        response = super().form_valid(form)

        log_audit(
            self.request,
            "login",
            app_label="auth",
            model_name="user",
            object_id=str(user.pk),
            object_repr=user.username,
            message=f"User logged in: {user.username}",
            old_values={},
            new_values=user_safe_values(user),
        )

        return response

    def get_success_url(self):
        return_url = get_role_redirect(self.request.user)
        return redirect(return_url).url


class SchoolLogoutView(LogoutView):
    next_page = "login"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user

            log_audit(
                request,
                "logout",
                app_label="auth",
                model_name="user",
                object_id=str(user.pk),
                object_repr=user.username,
                message=f"User logged out: {user.username}",
                old_values=user_safe_values(user),
                new_values={},
            )

        return super().dispatch(request, *args, **kwargs)


@login_required
def account_redirect(request):
    return redirect(get_role_redirect(request.user))


@permission_required("users.roles.view")
def user_role_list(request):
    users = User.objects.select_related("account_profile").order_by("username")

    query = request.GET.get("q", "").strip()
    role = request.GET.get("role", "").strip()

    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )

    if role:
        users = users.filter(account_profile__role=role)

    context = {
        "users": users,
        "query": query,
        "selected_role": role,
        "role_choices": UserProfile.ROLE_CHOICES,
    }

    return render(request, "accounts/user_role_list.html", context)


@permission_required("users.roles.manage")
def user_role_update(request, pk):
    user_obj = get_object_or_404(
        User.objects.select_related("account_profile"),
        pk=pk
    )

    if not hasattr(user_obj, "account_profile"):
        UserProfile.objects.create(user=user_obj)

    profile = user_obj.account_profile
    old_values = model_to_dict_safe(profile)

    if request.method == "POST":
        form = UserProfileRoleForm(request.POST, instance=profile)

        if form.is_valid():
            updated_profile = form.save()

            log_audit(
                request,
                "update",
                obj=updated_profile,
                message=f"Updated user role/profile for: {user_obj.username}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_profile),
            )

            messages.success(request, "User role updated successfully.")
            return redirect("user_role_list")

        messages.error(request, "Please correct the role form.")
    else:
        form = UserProfileRoleForm(instance=profile)

    return render(request, "accounts/user_role_form.html", {
        "form": form,
        "user_obj": user_obj,
    })



@permission_required("users.password.reset")
def user_reset_password(request, pk):
    user_obj = get_object_or_404(
        User.objects.select_related("account_profile"),
        pk=pk
    )

    if user_obj.is_superuser and not request.user.is_superuser:
        messages.error(request, "Only a superuser can reset another superuser password.")
        return redirect("user_role_list")

    if request.method == "POST":
        form = AdminUserPasswordResetForm(request.POST)

        if form.is_valid():
            old_values = user_safe_values(user_obj)

            new_password = form.cleaned_data["new_password"]
            must_change_password = form.cleaned_data.get("must_change_password", True)

            user_obj.set_password(new_password)
            user_obj.save(update_fields=["password"])

            profile = getattr(user_obj, "account_profile", None)

            if profile:
                profile.must_change_password = must_change_password
                profile.save(update_fields=["must_change_password"])

            new_values = user_safe_values(user_obj)
            new_values["password"] = "Password was reset by admin"
            new_values["must_change_password"] = str(must_change_password)

            log_audit(
                request,
                "update",
                app_label="auth",
                model_name="user",
                object_id=str(user_obj.pk),
                object_repr=user_obj.username,
                message=f"Admin reset password for user: {user_obj.username}",
                old_values=old_values,
                new_values=new_values,
            )

            messages.success(
                request,
                f"Password for {user_obj.username} was reset successfully."
            )
            return redirect("user_role_list")

        messages.error(request, "Please correct the password form.")
    else:
        form = AdminUserPasswordResetForm()

    return render(request, "accounts/user_reset_password.html", {
        "form": form,
        "user_obj": user_obj,
    })

@permission_required("parent.portal.view")
def parent_portal_home(request):
    parent = getattr(request.user, "parent_guardian_profile", None)

    students = []

    if parent:
        students = parent.students.select_related(
            "class_level",
            "stream",
        ).all()

    return render(request, "accounts/parent_portal_home.html", {
        "parent": parent,
        "students": students,
    })


def get_parent_student_or_404(request, student_id):
    parent = getattr(request.user, "parent_guardian_profile", None)

    if not parent:
        messages.error(request, "Parent profile not found.")
        return None, None

    student = get_object_or_404(
        parent.students.select_related(
            "class_level",
            "stream",
            "parent_guardian",
        ),
        pk=student_id
    )

    return parent, student

@permission_required("parent.invoices.view")
def parent_student_invoices(request, student_id):
    parent, student = get_parent_student_or_404(request, student_id)

    if not student:
        return redirect("parent_portal_home")

    invoices = StudentInvoice.objects.filter(
        student=student
    ).select_related(
        "academic_year",
        "term",
    ).prefetch_related(
        "items",
        "items__category",
        "payments",
        "payments__fee_item",
    ).order_by("-invoice_date", "-id")

    for invoice in invoices:
        if not invoice.items.exists() and invoice.status != "cancelled":
            sync_invoice_items_from_fee_structure(invoice)

        invoice.parent_total = invoice.total_amount
        invoice.parent_discount = invoice.discount_amount
        invoice.parent_paid_total = invoice.paid_amount
        invoice.parent_balance = invoice.balance
        invoice.parent_status = invoice.status
        invoice.parent_fee_breakdown = build_invoice_fee_breakdown(invoice)

    return render(request, "accounts/parent_student_invoices.html", {
        "parent": parent,
        "student": student,
        "invoices": invoices,
    })


@permission_required("parent.payments.view")
def parent_student_payments(request, student_id):
    parent, student = get_parent_student_or_404(request, student_id)

    if not student:
        return redirect("parent_portal_home")

    payments = FeePayment.objects.filter(
        invoice__student=student
    ).select_related(
        "invoice",
        "invoice__academic_year",
        "invoice__term",
    ).order_by("-payment_date", "-id")

    return render(request, "accounts/parent_student_payments.html", {
        "parent": parent,
        "student": student,
        "payments": payments,
    })


@permission_required("parent.results.view")
def parent_student_results(request, student_id):
    parent, student = get_parent_student_or_404(request, student_id)

    if not student:
        return redirect("parent_portal_home")

    student_exam_results = ExamResult.objects.filter(
        student=student,
        exam__isnull=False
    ).select_related(
        "exam",
        "exam__exam_type",
        "exam__academic_year",
        "exam__term",
    ).order_by(
        "-exam__start_date",
        "-exam_id",
    )

    exam_options = []
    used_exam_ids = set()

    for result in student_exam_results:
        if result.exam_id and result.exam_id not in used_exam_ids:
            used_exam_ids.add(result.exam_id)
            exam_options.append(result.exam)

    selected_exam_id = request.GET.get("exam", "").strip()

    if not selected_exam_id and exam_options:
        selected_exam_id = str(exam_options[0].id)

    selected_exam = None
    results = ExamResult.objects.none()

    total_marks = 0
    subject_count = 0
    average_marks = 0
    class_position = None
    total_students = 0
    highest_total = 0

    if selected_exam_id:
        results = ExamResult.objects.filter(
            student=student,
            exam_id=selected_exam_id
        ).select_related(
            "exam",
            "exam__exam_type",
            "exam__academic_year",
            "exam__term",
            "subject",
            "teacher",
        ).order_by(
            "subject__name",
        )

        selected_exam = results.first().exam if results.exists() else None

        summary = results.aggregate(
            total=Sum("marks"),
            subjects=Count("id"),
        )

        total_marks = summary["total"] or 0
        subject_count = summary["subjects"] or 0

        if subject_count:
            average_marks = total_marks / subject_count

        class_results = ExamResult.objects.filter(
            exam_id=selected_exam_id,
            student__class_level=student.class_level,
        )

        if student.stream:
            class_results = class_results.filter(student__stream=student.stream)

        rankings = list(
            class_results.values(
                "student_id"
            ).annotate(
                total=Sum("marks"),
                subjects=Count("id"),
            ).order_by(
                "-total",
                "student_id",
            )
        )

        total_students = len(rankings)

        if rankings:
            highest_total = rankings[0]["total"] or 0

        for index, item in enumerate(rankings, start=1):
            if item["student_id"] == student.id:
                class_position = index
                break

    return render(request, "accounts/parent_student_results.html", {
        "parent": parent,
        "student": student,
        "results": results,
        "exam_options": exam_options,
        "selected_exam_id": selected_exam_id,
        "selected_exam": selected_exam,
        "total_marks": total_marks,
        "subject_count": subject_count,
        "average_marks": average_marks,
        "class_position": class_position,
        "total_students": total_students,
        "highest_total": highest_total,
    })


@permission_required("parent.attendance.view")
def parent_student_attendance(request, student_id):
    parent, student = get_parent_student_or_404(request, student_id)

    if not student:
        return redirect("parent_portal_home")

    today = timezone.localdate()

    attendance_records = StudentAttendance.objects.filter(
        student=student
    ).order_by("-date")

    return render(request, "accounts/parent_student_attendance.html", {
        "parent": parent,
        "student": student,
        "attendance_records": attendance_records,
        "today": today,
    })


@permission_required("parents.login.manage")
def create_parent_login(request, pk):
    parent = get_object_or_404(ParentGuardian, pk=pk)

    if parent.user:
        messages.warning(request, "This parent already has a login account.")
        return redirect("parent_list")

    old_parent_values = model_to_dict_safe(parent)

    if request.method == "POST":
        form = CreateParentLoginForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
                email=parent.email or "",
                first_name=parent.full_name,
            )

            profile = user.account_profile
            old_profile_values = model_to_dict_safe(profile)

            profile.role = "parent"
            profile.phone = parent.phone
            profile.save()

            parent.user = user
            parent.save()

            log_audit(
                request,
                "create",
                app_label="auth",
                model_name="user",
                object_id=str(user.pk),
                object_repr=user.username,
                message=f"Created parent login user account for: {parent.full_name}",
                old_values={},
                new_values=user_safe_values(user),
            )

            log_audit(
                request,
                "update",
                obj=profile,
                message=f"Updated new parent user profile for: {user.username}",
                old_values=old_profile_values,
                new_values=model_to_dict_safe(profile),
            )

            log_audit(
                request,
                "update",
                obj=parent,
                message=f"Linked parent / guardian to login user: {user.username}",
                old_values=old_parent_values,
                new_values=model_to_dict_safe(parent),
            )

            messages.success(request, "Parent login account created successfully.")
            return redirect("parent_list")

        messages.error(request, "Please correct the parent login form.")
    else:
        form = CreateParentLoginForm()

    return render(request, "accounts/create_parent_login.html", {
        "form": form,
        "parent": parent,
    })