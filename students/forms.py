from django import forms
from .models import ParentGuardian, Student


class ParentGuardianForm(forms.ModelForm):
    class Meta:
        model = ParentGuardian
        fields = [
            "full_name",
            "relationship",
            "phone",
            "alternative_phone",
            "email",
            "address",
            "occupation",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Parent / guardian full name"}),
            "relationship": forms.Select(attrs={"class": "form-select"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+255..."}),
            "alternative_phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Optional"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Optional email"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "occupation": forms.TextInput(attrs={"class": "form-control", "placeholder": "Optional"}),
        }


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "admission_number",
            "first_name",
            "middle_name",
            "last_name",
            "gender",
            "date_of_birth",
            "class_level",
            "stream",
            "parent_guardian",
            "boarding_status",
            "previous_school",
            "medical_notes",
            "address",
            "photo",
            "status",
            "admission_date",
        ]

        widgets = {
            "admission_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Example: SLA-0001"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "middle_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "class_level": forms.Select(attrs={"class": "form-select"}),
            "stream": forms.Select(attrs={"class": "form-select"}),
            "parent_guardian": forms.Select(attrs={"class": "form-select"}),
            "boarding_status": forms.Select(attrs={"class": "form-select"}),
            "previous_school": forms.TextInput(attrs={"class": "form-control"}),
            "medical_notes": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "admission_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }