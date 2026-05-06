from django import forms
from django.contrib.auth.models import User

from accounts.models import UserProfile
from .models import StaffProfile


class StaffProfileForm(forms.ModelForm):
    create_login_account = forms.BooleanField(
        required=False,
        label="Create login account for this staff",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    username = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Optional login username"
        })
    )

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Optional login password"
        })
    )

    class Meta:
        model = StaffProfile
        fields = [
            "staff_id",
            "first_name",
            "middle_name",
            "last_name",
            "role",
            "gender",
            "date_of_birth",
            "phone",
            "alternative_phone",
            "email",
            "address",
            "qualification",
            "employment_date",
            "assigned_classes",
            "subjects",
            "salary",
            "photo",
            "status",
        ]

        widgets = {
            "staff_id": forms.TextInput(attrs={"class": "form-control", "placeholder": "Example: TCH-0001"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "middle_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),

            "role": forms.Select(attrs={"class": "form-select"}),
            "gender": forms.Select(attrs={"class": "form-select"}),

            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+255..."}),
            "alternative_phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),

            "address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "qualification": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Diploma / Degree / Certificate"
            }),
            "employment_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),

            "assigned_classes": forms.SelectMultiple(attrs={"class": "form-select", "size": 6}),
            "subjects": forms.SelectMultiple(attrs={"class": "form-select", "size": 6}),

            "salary": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def clean(self):
        cleaned_data = super().clean()

        create_login = cleaned_data.get("create_login_account")
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if create_login:
            if not username:
                self.add_error("username", "Username is required when creating a login account.")

            if not password:
                self.add_error("password", "Password is required when creating a login account.")

            qs = User.objects.filter(username=username)

            if self.instance and self.instance.user:
                qs = qs.exclude(pk=self.instance.user.pk)

            if username and qs.exists():
                self.add_error("username", "This username already exists.")

        return cleaned_data

    def save(self, commit=True):
        staff = super().save(commit=False)

        create_login = self.cleaned_data.get("create_login_account")
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if commit:
            staff.save()
            self.save_m2m()

        if create_login and username and password:
            if staff.user:
                user = staff.user
                user.username = username
                user.email = staff.email or ""
                user.first_name = staff.first_name
                user.last_name = staff.last_name
                user.set_password(password)
                user.save()
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=staff.email or "",
                    first_name=staff.first_name,
                    last_name=staff.last_name,
                )

                staff.user = user
                staff.save(update_fields=["user"])

            profile, created = UserProfile.objects.get_or_create(user=user)

            profile.role = staff.role
            profile.phone = staff.phone
            profile.is_active_profile = True
            profile.save()

        elif staff.user:
            profile, created = UserProfile.objects.get_or_create(user=staff.user)
            profile.role = staff.role
            profile.phone = staff.phone
            profile.is_active_profile = True
            profile.save()

        return staff