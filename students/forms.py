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
            "full_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Parent / guardian full name",
            }),
            "relationship": forms.Select(attrs={
                "class": "form-select",
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "+255...",
            }),
            "alternative_phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Optional",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Optional email",
            }),
            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
            }),
            "occupation": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Optional",
            }),
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
            "admission_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: SLA-0001",
            }),
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
            }),
            "middle_name": forms.TextInput(attrs={
                "class": "form-control",
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control",
            }),
            "gender": forms.Select(attrs={
                "class": "form-select",
            }),
            "date_of_birth": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),

            # Keep these normal because they are not too many.
            "class_level": forms.Select(attrs={
                "class": "form-select",
            }),
            "stream": forms.Select(attrs={
                "class": "form-select",
            }),

            # Searchable because parents can be many.
            "parent_guardian": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search parent by name or phone...",
            }),

            "boarding_status": forms.Select(attrs={
                "class": "form-select",
            }),
            "previous_school": forms.TextInput(attrs={
                "class": "form-control",
            }),
            "medical_notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
            }),
            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
            }),
            "photo": forms.ClearableFileInput(attrs={
                "class": "form-control",
            }),
            "status": forms.Select(attrs={
                "class": "form-select",
            }),
            "admission_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Normal dropdown labels
        if "class_level" in self.fields:
            self.fields["class_level"].empty_label = "Select class"

        if "stream" in self.fields:
            self.fields["stream"].empty_label = "Select stream"

        # Searchable dropdown label
        if "parent_guardian" in self.fields:
            self.fields["parent_guardian"].empty_label = "Search / select parent"