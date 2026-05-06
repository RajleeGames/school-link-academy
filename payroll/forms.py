from django import forms
from django.utils import timezone

from .models import PayrollRecord, SalaryStructure


class SalaryStructureForm(forms.ModelForm):
    class Meta:
        model = SalaryStructure
        fields = [
            "staff",
            "basic_salary",
            "transport_allowance",
            "housing_allowance",
            "medical_allowance",
            "other_allowance",
            "tax_deduction",
            "loan_deduction",
            "other_deduction",
            "is_active",
            "notes",
        ]

        widgets = {
            "staff": forms.Select(attrs={
                "class": "form-select"
            }),
            "basic_salary": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0,
                "placeholder": "Basic salary"
            }),
            "transport_allowance": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0
            }),
            "housing_allowance": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0
            }),
            "medical_allowance": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0
            }),
            "other_allowance": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0
            }),
            "tax_deduction": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0
            }),
            "loan_deduction": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0
            }),
            "other_deduction": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Optional notes"
            }),
        }


class PayrollRecordForm(forms.ModelForm):
    class Meta:
        model = PayrollRecord
        fields = [
            "staff",
            "month",
            "year",
            "basic_salary",
            "total_allowances",
            "total_deductions",
            "net_salary",
            "payment_date",
            "payment_method",
            "reference",
            "status",
            "notes",
        ]

        widgets = {
            "staff": forms.Select(attrs={
                "class": "form-select"
            }),
            "month": forms.Select(attrs={
                "class": "form-select"
            }),
            "year": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 2000
            }),
            "basic_salary": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0
            }),
            "total_allowances": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0
            }),
            "total_deductions": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0
            }),
            "net_salary": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0
            }),
            "payment_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "payment_method": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Cash / Bank / Mobile Money"
            }),
            "reference": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Payment reference"
            }),
            "status": forms.Select(attrs={
                "class": "form-select"
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Optional notes"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.initial.get("year"):
            self.initial["year"] = timezone.localdate().year


class PayrollGenerateForm(forms.Form):
    month = forms.ChoiceField(
        choices=PayrollRecord.MONTH_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-select"
        })
    )

    year = forms.IntegerField(
        initial=timezone.localdate().year,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "min": 2000
        })
    )