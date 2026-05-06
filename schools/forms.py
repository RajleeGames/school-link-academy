from django import forms
from django.contrib.auth.models import User

from .models import SchoolBranch, SchoolProfile, SystemSetting


class SchoolProfileForm(forms.ModelForm):
    class Meta:
        model = SchoolProfile
        fields = [
            "name",
            "short_name",
            "motto",
            "registration_number",
            "school_type",
            "school_mode",
            "phone",
            "email",
            "website",
            "address",
            "logo",
            "currency",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Example: School Link Academy"}),
            "short_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Example: SLA"}),
            "motto": forms.TextInput(attrs={"class": "form-control", "placeholder": "Example: Education for Excellence"}),
            "registration_number": forms.TextInput(attrs={"class": "form-control"}),
            "school_type": forms.Select(attrs={"class": "form-select"}),
            "school_mode": forms.Select(attrs={"class": "form-select"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+255..."}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "website": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://example.com"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "logo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "currency": forms.TextInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class SchoolBranchForm(forms.ModelForm):
    class Meta:
        model = SchoolBranch
        fields = [
            "name",
            "code",
            "phone",
            "email",
            "address",
            "manager_name",
            "is_main_branch",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Example: Main Campus"}),
            "code": forms.TextInput(attrs={"class": "form-control", "placeholder": "Example: MAIN"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+255..."}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "manager_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Branch manager"}),
            "is_main_branch": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class SystemSettingForm(forms.ModelForm):
    class Meta:
        model = SystemSetting
        fields = [
            "default_currency",
            "academic_year_auto_create",
            "enable_sms_notifications",
            "enable_email_notifications",
            "enable_parent_portal",
            "enable_student_portal",
            "attendance_mode",
            "receipt_prefix",
            "invoice_prefix",
            "admission_prefix",
            "low_stock_alert_level",
        ]

        widgets = {
            "default_currency": forms.TextInput(attrs={"class": "form-control"}),
            "academic_year_auto_create": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "enable_sms_notifications": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "enable_email_notifications": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "enable_parent_portal": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "enable_student_portal": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "attendance_mode": forms.Select(attrs={"class": "form-select"}),
            "receipt_prefix": forms.TextInput(attrs={"class": "form-control"}),
            "invoice_prefix": forms.TextInput(attrs={"class": "form-control"}),
            "admission_prefix": forms.TextInput(attrs={"class": "form-control"}),
            "low_stock_alert_level": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        }


class UserPermissionForm(forms.ModelForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
    is_staff = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
    is_superuser = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))

    class Meta:
        model = User
        fields = ["is_active", "is_staff", "is_superuser"]