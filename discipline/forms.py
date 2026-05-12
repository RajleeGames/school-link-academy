from django import forms

from .models import DisciplineCategory, DisciplineRecord, DisciplineFollowUp


class DisciplineCategoryForm(forms.ModelForm):
    class Meta:
        model = DisciplineCategory
        fields = [
            "name",
            "category_type",
            "description",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Late Coming, Fighting, Excellent Conduct",
            }),
            "category_type": forms.Select(attrs={
                "class": "form-select",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Optional description",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
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
            # Searchable because students can become many.
            "student": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search student by name or admission number...",
            }),

            "record_type": forms.Select(attrs={
                "class": "form-select",
            }),

            # Category can remain normal unless you create many discipline categories.
            "category": forms.Select(attrs={
                "class": "form-select",
            }),

            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Late coming to school",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Explain what happened clearly",
            }),
            "incident_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "incident_time": forms.TimeInput(attrs={
                "class": "form-control",
                "type": "time",
            }),
            "severity": forms.Select(attrs={
                "class": "form-select",
            }),
            "action_taken": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Action taken by school",
            }),

            # Searchable because staff/teachers can become many.
            "reported_by": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search staff / teacher...",
            }),

            "parent_notified": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
            "parent_feedback": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Parent feedback, if any",
            }),
            "status": forms.Select(attrs={
                "class": "form-select",
            }),
            "attachment": forms.ClearableFileInput(attrs={
                "class": "form-control",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "student" in self.fields:
            self.fields["student"].empty_label = "Search / select student"

        if "category" in self.fields:
            self.fields["category"].empty_label = "Select category"

        if "reported_by" in self.fields:
            self.fields["reported_by"].empty_label = "Search / select reporter"


class DisciplineFollowUpForm(forms.ModelForm):
    class Meta:
        model = DisciplineFollowUp
        fields = [
            "record",
            "follow_up_date",
            "note",
            "handled_by",
            "next_action",
        ]

        widgets = {
            # Searchable because discipline records can become many.
            "record": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search discipline record...",
            }),
            "follow_up_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "note": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Write follow-up note",
            }),

            # Searchable because staff/teachers can become many.
            "handled_by": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search staff / teacher...",
            }),

            "next_action": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Parent meeting next week",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "record" in self.fields:
            self.fields["record"].empty_label = "Search / select record"

        if "handled_by" in self.fields:
            self.fields["handled_by"].empty_label = "Search / select staff"