from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import render

from accounts.decorators import permission_required
from accounts.permissions import get_user_role, user_has_permission

from academics.models import ClassLevel, Stream, Subject
from students.models import ParentGuardian, Student
from staff.models import StaffProfile
from fees.models import FeePayment, StudentInvoice
from expenses.models import Expense


def _zero_money():
    return Decimal("0.00")


@permission_required("dashboard.view")
def dashboard_home(request):
    role = get_user_role(request.user)

    can_view_students = user_has_permission(request.user, "students.view")
    can_view_parents = user_has_permission(request.user, "parents.view")
    can_view_staff = user_has_permission(request.user, "staff.view")
    can_view_academics = user_has_permission(request.user, "academics.view")
    can_view_subjects = user_has_permission(request.user, "subjects.view")

    can_view_fees = user_has_permission(request.user, "fees.view")
    can_view_payments = user_has_permission(request.user, "payments.view")
    can_view_expenses = user_has_permission(request.user, "expenses.view")
    can_view_reports = user_has_permission(request.user, "reports.view")

    total_students = 0
    active_students = 0
    recent_students = []

    total_parents = 0

    total_teachers = 0
    total_staff = 0
    active_staff = 0
    recent_staff = []

    total_classes = 0
    total_streams = 0
    total_subjects = 0

    total_fees_paid = _zero_money()
    total_expenses = _zero_money()
    net_cash = _zero_money()
    total_debtors = 0
    outstanding_fees = _zero_money()
    recent_payments = []
    recent_expenses = []

    teacher_profile = None
    teacher_classes = []
    teacher_subjects = []

    if can_view_students:
        total_students = Student.objects.count()
        active_students = Student.objects.filter(status="active").count()

        recent_students = Student.objects.select_related(
            "class_level",
            "stream",
            "parent_guardian"
        ).order_by("-created_at")[:5]

    if can_view_parents:
        total_parents = ParentGuardian.objects.count()

    if can_view_staff:
        total_teachers = StaffProfile.objects.filter(role="teacher").count()
        total_staff = StaffProfile.objects.count()
        active_staff = StaffProfile.objects.filter(status="active").count()
        recent_staff = StaffProfile.objects.order_by("-created_at")[:5]

    if can_view_academics:
        total_classes = ClassLevel.objects.count()
        total_streams = Stream.objects.count()

    if can_view_subjects:
        total_subjects = Subject.objects.count()

    if can_view_payments:
        total_fees_paid = FeePayment.objects.filter(status="confirmed").aggregate(
            total=Sum("amount")
        )["total"] or _zero_money()

        recent_payments = FeePayment.objects.select_related(
            "invoice",
            "invoice__student"
        ).order_by("-created_at")[:5]

    if can_view_expenses:
        total_expenses = Expense.objects.filter(status="paid").aggregate(
            total=Sum("amount")
        )["total"] or _zero_money()

        recent_expenses = Expense.objects.select_related(
            "category"
        ).order_by("-created_at")[:5]

    if can_view_payments or can_view_expenses:
        net_cash = total_fees_paid - total_expenses

    if can_view_fees:
        total_debtors = StudentInvoice.objects.exclude(
            status__in=["paid", "cancelled"]
        ).values("student").distinct().count()

        unpaid_invoices = StudentInvoice.objects.exclude(
            status__in=["paid", "cancelled"]
        )

        for invoice in unpaid_invoices:
            outstanding_fees += invoice.balance

    if role == "teacher":
        teacher_profile = StaffProfile.objects.filter(user=request.user).prefetch_related(
            "assigned_classes",
            "subjects"
        ).first()

        if teacher_profile:
            teacher_classes = teacher_profile.assigned_classes.all()
            teacher_subjects = teacher_profile.subjects.all()

    context = {
        "role": role,

        "can_view_students": can_view_students,
        "can_view_parents": can_view_parents,
        "can_view_staff": can_view_staff,
        "can_view_academics": can_view_academics,
        "can_view_subjects": can_view_subjects,
        "can_view_fees": can_view_fees,
        "can_view_payments": can_view_payments,
        "can_view_expenses": can_view_expenses,
        "can_view_reports": can_view_reports,

        "total_students": total_students,
        "total_parents": total_parents,
        "total_teachers": total_teachers,
        "total_staff": total_staff,

        "total_classes": total_classes,
        "total_streams": total_streams,
        "total_subjects": total_subjects,

        "active_students": active_students,
        "active_staff": active_staff,

        "total_fees_paid": total_fees_paid,
        "total_expenses": total_expenses,
        "net_cash": net_cash,
        "total_debtors": total_debtors,
        "outstanding_fees": outstanding_fees,

        "recent_students": recent_students,
        "recent_staff": recent_staff,
        "recent_payments": recent_payments,
        "recent_expenses": recent_expenses,

        "teacher_profile": teacher_profile,
        "teacher_classes": teacher_classes,
        "teacher_subjects": teacher_subjects,
    }

    return render(request, "dashboard/home.html", context)