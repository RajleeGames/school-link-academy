from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import permission_required

from .forms import (
    SchoolBranchForm,
    SchoolProfileForm,
    SystemSettingForm,
    UserPermissionForm,
)
from .models import SchoolBranch, SchoolProfile, SystemSetting


@permission_required("school.profile.view")
def school_profile(request):
    profile = SchoolProfile.objects.first()

    if request.method == "POST":
        if not request.user.is_superuser and "school.profile.edit" not in getattr(request, "current_user_permissions", []):
            messages.error(request, "You are not allowed to edit the school profile.")
            return redirect("school_profile")

        form = SchoolProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            form.save()
            messages.success(request, "School profile saved successfully.")
            return redirect("school_profile")

        messages.error(request, "Please correct the school profile form.")
    else:
        form = SchoolProfileForm(instance=profile)

    return render(request, "schools/profile.html", {
        "form": form,
        "profile": profile,
    })


@permission_required("school.branches.view")
def school_branch_list(request):
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    branches = SchoolBranch.objects.all()

    if query:
        branches = branches.filter(
            Q(name__icontains=query)
            | Q(code__icontains=query)
            | Q(phone__icontains=query)
            | Q(manager_name__icontains=query)
        )

    if status == "active":
        branches = branches.filter(is_active=True)

    if status == "inactive":
        branches = branches.filter(is_active=False)

    return render(request, "schools/branch_list.html", {
        "branches": branches,
        "query": query,
        "status": status,
    })


@permission_required("school.branches.manage")
def school_branch_create(request):
    if request.method == "POST":
        form = SchoolBranchForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "School branch added successfully.")
            return redirect("school_branch_list")

        messages.error(request, "Please correct the branch form.")
    else:
        form = SchoolBranchForm()

    return render(request, "schools/branch_form.html", {
        "form": form,
        "title": "Add School Branch",
        "button_text": "Save Branch",
    })


@permission_required("school.branches.manage")
def school_branch_update(request, pk):
    branch = get_object_or_404(SchoolBranch, pk=pk)

    if request.method == "POST":
        form = SchoolBranchForm(request.POST, instance=branch)

        if form.is_valid():
            form.save()
            messages.success(request, "School branch updated successfully.")
            return redirect("school_branch_list")

        messages.error(request, "Please correct the branch form.")
    else:
        form = SchoolBranchForm(instance=branch)

    return render(request, "schools/branch_form.html", {
        "form": form,
        "title": "Edit School Branch",
        "button_text": "Update Branch",
    })


@permission_required("school.settings.manage")
def system_settings(request):
    settings_obj = SystemSetting.objects.first()

    if request.method == "POST":
        form = SystemSettingForm(request.POST, instance=settings_obj)

        if form.is_valid():
            form.save()
            messages.success(request, "System settings saved successfully.")
            return redirect("system_settings")

        messages.error(request, "Please correct the system settings form.")
    else:
        form = SystemSettingForm(instance=settings_obj)

    return render(request, "schools/system_settings.html", {
        "form": form,
        "settings_obj": settings_obj,
    })


@permission_required("users.roles.view")
def user_permissions(request):
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    users = User.objects.all().order_by("username")

    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )

    if status == "active":
        users = users.filter(is_active=True)

    if status == "inactive":
        users = users.filter(is_active=False)

    if status == "staff":
        users = users.filter(is_staff=True)

    if status == "superuser":
        users = users.filter(is_superuser=True)

    return render(request, "schools/user_permissions.html", {
        "users": users,
        "query": query,
        "status": status,
    })


@permission_required("users.roles.manage")
def user_permission_update(request, pk):
    user_obj = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        form = UserPermissionForm(request.POST, instance=user_obj)

        if form.is_valid():
            form.save()
            messages.success(request, "User permissions updated successfully.")
            return redirect("user_permissions")

        messages.error(request, "Please correct the permission form.")
    else:
        form = UserPermissionForm(instance=user_obj)

    return render(request, "schools/user_permission_form.html", {
        "form": form,
        "user_obj": user_obj,
    })