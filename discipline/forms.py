from django import forms
from .models import DisciplineCategory, DisciplineRecord, DisciplineFollowUp


class DisciplineCategoryForm(forms.ModelForm):
    class Meta:
        model = DisciplineCategory
        fields = ["name", "category_type", "description", "is_active"]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Late Coming, Fighting, Excellent Conduct"
            }),
            "category_type": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Optional description"
            }),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class DisciplineRecordForm(forms.ModelForm):
    class Meta:
        model = DisciplineRecord
        fields = [
            "student",
            "record_type",
            "category",
            "title",
            "description",
            "incident_date",
            "incident_time",
            "severity",
            "action_taken",
            "reported_by",
            "parent_notified",
            "parent_feedback",
            "status",
            "attachment",
        ]

        widgets = {
            "student": forms.Select(attrs={"class": "form-select"}),
            "record_type": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Late coming to school"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Explain what happened clearly"
            }),
            "incident_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "incident_time": forms.TimeInput(attrs={
                "class": "form-control",
                "type": "time"
            }),
            "severity": forms.Select(attrs={"class": "form-select"}),
            "action_taken": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Action taken by school"
            }),
            "reported_by": forms.Select(attrs={"class": "form-select"}),
            "parent_notified": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "parent_feedback": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Parent feedback, if any"
            }),
            "status": forms.Select(attrs={"class": "form-select"}),
            "attachment": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class DisciplineFollowUpForm(forms.ModelForm):
    class Meta:
        model = DisciplineFollowUp
        fields = ["record", "follow_up_date", "note", "handled_by", "next_action"]

        widgets = {
            "record": forms.Select(attrs={"class": "form-select"}),
            "follow_up_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "note": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Write follow-up note"
            }),
            "handled_by": forms.Select(attrs={"class": "form-select"}),
            "next_action": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Parent meeting next week"
            }),
        }