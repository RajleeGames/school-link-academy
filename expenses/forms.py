from django import forms
from .models import ExpenseCategory, Expense


class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ["name", "description", "is_active"]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Salaries, Food, Transport, Utilities"
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


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            "expense_number",
            "category",
            "title",
            "description",
            "amount",
            "expense_date",
            "payment_method",
            "reference",
            "paid_to",
            "recorded_by",
            "status",
            "receipt_file",
        ]

        widgets = {
            "expense_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: EXP-00001"
            }),
            "category": forms.Select(attrs={
                "class": "form-select"
            }),
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Teacher salary payment"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Optional notes"
            }),
            "amount": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "placeholder": "0.00"
            }),
            "expense_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "payment_method": forms.Select(attrs={
                "class": "form-select"
            }),
            "reference": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Transaction reference optional"
            }),
            "paid_to": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Person/company paid"
            }),
            "recorded_by": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Recorder name"
            }),
            "status": forms.Select(attrs={
                "class": "form-select"
            }),
            "receipt_file": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
        }