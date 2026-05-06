from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from attendance.models import StudentAttendance
from exams.models import ExamResult
from fees.models import FeePayment, StudentInvoice
from students.models import ParentGuardian

from accounts.decorators import permission_required
from accounts.permissions import user_has_permission

from .forms import CreateParentLoginForm, SchoolLoginForm, UserProfileRoleForm
from .models import UserProfile


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
            messages.error(
                self.request,
                "Your account is inactive. Contact administrator."
            )
            return redirect("login")

        return super().form_valid(form)

    def get_success_url(self):
        return_url = get_role_redirect(self.request.user)
        return redirect(return_url).url


class SchoolLogoutView(LogoutView):
    next_page = "login"


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

    if request.method == "POST":
        form = UserProfileRoleForm(request.POST, instance=profile)

        if form.is_valid():
            form.save()
            messages.success(request, "User role updated successfully.")
            return redirect("user_role_list")

        messages.error(request, "Please correct the role form.")
    else:
        form = UserProfileRoleForm(instance=profile)

    return render(request, "accounts/user_role_form.html", {
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
        "payments",
    ).order_by("-invoice_date", "-id")

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

    results = ExamResult.objects.filter(
        student=student
    ).select_related(
        "exam",
        "exam__exam_type",
        "exam__academic_year",
        "exam__term",
        "subject",
        "teacher",
    ).order_by(
        "-exam__start_date",
        "subject__name",
    )

    return render(request, "accounts/parent_student_results.html", {
        "parent": parent,
        "student": student,
        "results": results,
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
            profile.role = "parent"
            profile.phone = parent.phone
            profile.save()

            parent.user = user
            parent.save()

            messages.success(request, "Parent login account created successfully.")
            return redirect("parent_list")

        messages.error(request, "Please correct the parent login form.")
    else:
        form = CreateParentLoginForm()

    return render(request, "accounts/create_parent_login.html", {
        "form": form,
        "parent": parent,
    })