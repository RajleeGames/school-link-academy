from django import forms
from .models import AcademicYear, Term, ClassLevel, Stream, Subject


class AcademicYearForm(forms.ModelForm):
    class Meta:
        model = AcademicYear
        fields = ["name", "start_date", "end_date", "is_current"]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Example: 2026"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "is_current": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class TermForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = ["academic_year", "name", "start_date", "end_date", "is_current"]

        widgets = {
            "academic_year": forms.Select(attrs={"class": "form-select"}),
            "name": forms.Select(attrs={"class": "form-select"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "is_current": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ClassLevelForm(forms.ModelForm):
    class Meta:
        model = ClassLevel
        fields = ["name", "level_type", "order", "is_active"]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Example: Form One / Standard One"}),
            "level_type": forms.Select(attrs={"class": "form-select"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class StreamForm(forms.ModelForm):
    class Meta:
        model = Stream
        fields = ["class_level", "name", "capacity", "is_active"]

        widgets = {
            "class_level": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Example: A / B / Science"}),
            "capacity": forms.NumberInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["name", "code", "subject_type", "class_levels", "is_active"]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Example: Mathematics"}),
            "code": forms.TextInput(attrs={"class": "form-control", "placeholder": "Example: MATH"}),
            "subject_type": forms.Select(attrs={"class": "form-select"}),
            "class_levels": forms.SelectMultiple(attrs={"class": "form-select", "size": 6}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }