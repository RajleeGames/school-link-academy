from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import UserProfile


class SchoolLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter username",
            "autofocus": True,
            "autocomplete": "username",
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter password",
            "autocomplete": "current-password",
        })
    )


class UserProfileRoleForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "role",
            "phone",
            "must_change_password",
            "is_active_profile",
        ]

        widgets = {
            "role": forms.Select(attrs={"class": "form-select"}),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "+255..."
            }),
            "must_change_password": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
            "is_active_profile": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }


class CreateParentLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Parent username",
            "autocomplete": "username",
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Parent password",
            "autocomplete": "new-password",
        })
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm password",
            "autocomplete": "new-password",
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get("username")

        if username:
            username = username.strip()

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already used.")

        return username

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        if password:
            validate_password(password)

        return cleaned_data


class AdminUserPasswordResetForm(forms.Form):
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter new password",
            "autocomplete": "new-password",
        })
    )

    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm new password",
            "autocomplete": "new-password",
        })
    )

    must_change_password = forms.BooleanField(
        label="Require user to change password after login",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            "class": "form-check-input",
        })
    )

    def clean(self):
        cleaned_data = super().clean()

        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        if new_password:
            validate_password(new_password)

        return cleaned_data