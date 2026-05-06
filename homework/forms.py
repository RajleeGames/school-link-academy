from django import forms
from .models import Homework, HomeworkSubmission


class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = [
            "title",
            "description",
            "academic_year",
            "term",
            "class_level",
            "stream",
            "subject",
            "teacher",
            "assigned_date",
            "due_date",
            "attachment",
            "status",
            "is_active",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Mathematics exercise page 25"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Write homework instructions here"
            }),
            "academic_year": forms.Select(attrs={"class": "form-select"}),
            "term": forms.Select(attrs={"class": "form-select"}),
            "class_level": forms.Select(attrs={"class": "form-select"}),
            "stream": forms.Select(attrs={"class": "form-select"}),
            "subject": forms.Select(attrs={"class": "form-select"}),
            "teacher": forms.Select(attrs={"class": "form-select"}),
            "assigned_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "due_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "attachment": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class HomeworkSubmissionForm(forms.ModelForm):
    class Meta:
        model = HomeworkSubmission
        fields = [
            "homework",
            "student",
            "submitted_date",
            "submitted_file",
            "marks",
            "teacher_comment",
            "status",
        ]

        widgets = {
            "homework": forms.Select(attrs={"class": "form-select"}),
            "student": forms.Select(attrs={"class": "form-select"}),
            "submitted_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "submitted_file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "marks": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "placeholder": "Optional marks"
            }),
            "teacher_comment": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Teacher comment"
            }),
            "status": forms.Select(attrs={"class": "form-select"}),
        }