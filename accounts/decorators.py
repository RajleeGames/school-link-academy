# accounts/decorators.py

from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .permissions import user_has_any_permission, user_has_permission


def permission_required(permission_code):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if user_has_permission(request.user, permission_code):
                return view_func(request, *args, **kwargs)

            messages.error(request, "You are not allowed to view this page.")
            return render(
                request,
                "accounts/access_denied.html",
                {"permission_code": permission_code},
                status=403,
            )

        return wrapper

    return decorator


def any_permission_required(*permission_codes):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if user_has_any_permission(request.user, permission_codes):
                return view_func(request, *args, **kwargs)

            messages.error(request, "You are not allowed to view this page.")
            return render(
                request,
                "accounts/access_denied.html",
                {"permission_code": ", ".join(permission_codes)},
                status=403,
            )

        return wrapper

    return decorator


def staff_role_is(user, *roles):
    """
    Check user's staff role safely.
    Example:
    staff_role_is(request.user, "teacher", "accountant")
    """
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    staff_profile = getattr(user, "staff_profile", None)

    if not staff_profile:
        return False

    return staff_profile.role in roles


def user_staff_profile(user):
    """
    Return StaffProfile linked to the logged-in user.
    """
    if not user.is_authenticated:
        return None

    return getattr(user, "staff_profile", None)


def payroll_admin_required(user):
    """
    People allowed to see all payroll records.
    """
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if user_has_permission(user, "payroll.manage"):
        return True

    return staff_role_is(
        user,
        "accountant",
        "admin_staff",
        "head_teacher",
    )


def can_view_payroll_record(user, payroll_record):
    """
    Payroll privacy rule:
    - Admin/accountant/head teacher/payroll manager can view all.
    - Staff/teacher can view only their own payroll record.
    """
    if payroll_admin_required(user):
        return True

    staff_profile = user_staff_profile(user)

    if not staff_profile:
        return False

    return payroll_record.staff_id == staff_profile.id


def admin_required(view_func):
    return permission_required("users.roles.manage")(view_func)


def finance_required(view_func):
    return any_permission_required(
        "fees.view",
        "payments.view",
        "expenses.view",
    )(view_func)


def academic_required(view_func):
    return any_permission_required(
        "academics.view",
        "exams.view",
        "results.view",
    )(view_func)


def parent_required(view_func):
    return permission_required("parent.portal.view")(view_func)