from django import forms

from .models import ExamType, Exam, GradeScale, ExamResult


class ExamTypeForm(forms.ModelForm):
    class Meta:
        model = ExamType
        fields = ["name", "description", "is_active"]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Mid Term, Terminal, Annual",
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
                "placeholder": "Example: Form 1 Mid Term Exam",
            }),
            "exam_type": forms.Select(attrs={
                "class": "form-select",
            }),
            "academic_year": forms.Select(attrs={
                "class": "form-select",
            }),
            "term": forms.Select(attrs={
                "class": "form-select",
            }),
            "class_level": forms.Select(attrs={
                "class": "form-select",
            }),
            "start_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "end_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "status": forms.Select(attrs={
                "class": "form-select",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "exam_type" in self.fields:
            self.fields["exam_type"].empty_label = "Select exam type"

        if "academic_year" in self.fields:
            self.fields["academic_year"].empty_label = "Select academic year"

        if "term" in self.fields:
            self.fields["term"].empty_label = "Select term"

        if "class_level" in self.fields:
            self.fields["class_level"].empty_label = "Select class"


class GradeScaleForm(forms.ModelForm):
    class Meta:
        model = GradeScale
        fields = [
            "grade",
            "min_score",
            "max_score",
            "points",
            "remark",
            "is_active",
        ]

        widgets = {
            "grade": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "A, B, C, D, F",
            }),
            "min_score": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
                "max": "100",
            }),
            "max_score": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
                "max": "100",
            }),
            "points": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
            }),
            "remark": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Excellent, Good, Average...",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }


class ExamResultForm(forms.ModelForm):
    class Meta:
        model = ExamResult
        fields = [
            "exam",
            "student",
            "subject",
            "teacher",
            "marks",
        ]

        widgets = {
            # Searchable because exams can become many over years.
            "exam": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search exam...",
            }),

            # Searchable because students can become many.
            "student": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search student by name or admission number...",
            }),

            # Searchable because subjects can become many.
            "subject": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search subject...",
            }),

            # Searchable because teachers/staff can become many.
            "teacher": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search teacher...",
            }),

            "marks": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
                "max": "100",
                "placeholder": "Enter marks out of 100",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "exam" in self.fields:
            self.fields["exam"].empty_label = "Search / select exam"

        if "student" in self.fields:
            self.fields["student"].empty_label = "Search / select student"

        if "subject" in self.fields:
            self.fields["subject"].empty_label = "Search / select subject"

        if "teacher" in self.fields:
            self.fields["teacher"].empty_label = "Search / select teacher"