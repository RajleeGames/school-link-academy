from django import forms
from .models import StudentAttendance, StaffAttendance


class StudentAttendanceForm(forms.ModelForm):
    class Meta:
        model = StudentAttendance
        fields = ["student", "date", "status", "arrival_time", "remarks"]

        widgets = {
            "student": forms.Select(attrs={"class": "form-select"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "arrival_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "remarks": forms.TextInput(attrs={"class": "form-control", "placeholder": "Optional remarks"}),
        }


class StaffAttendanceForm(forms.ModelForm):
    class Meta:
        model = StaffAttendance
        fields = ["staff", "date", "status", "check_in_time", "check_out_time", "remarks"]

        widgets = {
            "staff": forms.Select(attrs={"class": "form-select"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "check_in_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "check_out_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "remarks": forms.TextInput(attrs={"class": "form-control", "placeholder": "Optional remarks"}),
        }