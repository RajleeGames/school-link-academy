from django import forms

from .models import StudentAttendance, StaffAttendance


class StudentAttendanceForm(forms.ModelForm):
    class Meta:
        model = StudentAttendance
        fields = [
            "student",
            "date",
            "status",
            "arrival_time",
            "remarks",
        ]

        widgets = {
            # Searchable because students can be many.
            "student": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search student by name or admission number...",
            }),

            "date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "status": forms.Select(attrs={
                "class": "form-select",
            }),
            "arrival_time": forms.TimeInput(attrs={
                "class": "form-control",
                "type": "time",
            }),
            "remarks": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Optional remarks",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "student" in self.fields:
            self.fields["student"].empty_label = "Search / select student"


class StaffAttendanceForm(forms.ModelForm):
    class Meta:
        model = StaffAttendance
        fields = [
            "staff",
            "date",
            "status",
            "check_in_time",
            "check_out_time",
            "remarks",
        ]

        widgets = {
            # Searchable because staff can be many.
            "staff": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search staff by name or staff ID...",
            }),

            "date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "status": forms.Select(attrs={
                "class": "form-select",
            }),
            "check_in_time": forms.TimeInput(attrs={
                "class": "form-control",
                "type": "time",
            }),
            "check_out_time": forms.TimeInput(attrs={
                "class": "form-control",
                "type": "time",
            }),
            "remarks": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Optional remarks",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "staff" in self.fields:
            self.fields["staff"].empty_label = "Search / select staff"