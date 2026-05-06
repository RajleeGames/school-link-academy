from django import forms
from .models import ExamType, Exam, GradeScale, ExamResult


class ExamTypeForm(forms.ModelForm):
    class Meta:
        model = ExamType
        fields = ["name", "description", "is_active"]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Mid Term, Terminal, Annual"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Optional description"
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = [
            "name",
            "exam_type",
            "academic_year",
            "term",
            "class_level",
            "start_date",
            "end_date",
            "status",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Form 1 Mid Term Exam"
            }),
            "exam_type": forms.Select(attrs={"class": "form-select"}),
            "academic_year": forms.Select(attrs={"class": "form-select"}),
            "term": forms.Select(attrs={"class": "form-select"}),
            "class_level": forms.Select(attrs={"class": "form-select"}),
            "start_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "end_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "status": forms.Select(attrs={"class": "form-select"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class GradeScaleForm(forms.ModelForm):
    class Meta:
        model = GradeScale
        fields = ["grade", "min_score", "max_score", "points", "remark", "is_active"]

        widgets = {
            "grade": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "A, B, C, D, F"
            }),
            "min_score": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01"
            }),
            "max_score": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01"
            }),
            "points": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01"
            }),
            "remark": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Excellent, Good, Average..."
            }),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ExamResultForm(forms.ModelForm):
    class Meta:
        model = ExamResult
        fields = ["exam", "student", "subject", "teacher", "marks"]

        widgets = {
            "exam": forms.Select(attrs={"class": "form-select"}),
            "student": forms.Select(attrs={"class": "form-select"}),
            "subject": forms.Select(attrs={"class": "form-select"}),
            "teacher": forms.Select(attrs={"class": "form-select"}),
            "marks": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
                "max": "100"
            }),
        }