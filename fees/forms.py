from django import forms
from .models import FeeCategory, FeeStructure, StudentInvoice, StudentInvoiceItem, FeePayment


class FeeCategoryForm(forms.ModelForm):
    class Meta:
        model = FeeCategory
        fields = ["name", "description", "is_active"]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Example: Tuition Fee"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = [
            "category",
            "academic_year",
            "term",
            "class_level",
            "amount",
            "is_required",
            "is_active",
        ]

        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "academic_year": forms.Select(attrs={"class": "form-select"}),
            "term": forms.Select(attrs={"class": "form-select"}),
            "class_level": forms.Select(attrs={"class": "form-select"}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "is_required": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class StudentInvoiceForm(forms.ModelForm):
    class Meta:
        model = StudentInvoice
        fields = [
            "student",
            "academic_year",
            "term",
            "invoice_number",
            "total_amount",
            "discount_amount",
            "invoice_date",
            "due_date",
            "notes",
        ]

        widgets = {
            "student": forms.Select(attrs={"class": "form-select"}),
            "academic_year": forms.Select(attrs={"class": "form-select"}),
            "term": forms.Select(attrs={"class": "form-select"}),
            "invoice_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Example: INV-0001"}),
            "total_amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "discount_amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "invoice_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "due_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }


class StudentInvoiceItemForm(forms.ModelForm):
    class Meta:
        model = StudentInvoiceItem
        fields = ["category", "description", "amount"]

        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "description": forms.TextInput(attrs={"class": "form-control"}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }


class FeePaymentForm(forms.ModelForm):
    class Meta:
        model = FeePayment
        fields = [
            "invoice",
            "receipt_number",
            "payment_date",
            "amount",
            "method",
            "reference",
            "status",
            "received_by",
            "notes",
        ]

        widgets = {
            "invoice": forms.Select(attrs={"class": "form-select"}),
            "receipt_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Example: REC-0001"}),
            "payment_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "method": forms.Select(attrs={"class": "form-select"}),
            "reference": forms.TextInput(attrs={"class": "form-control", "placeholder": "Transaction reference"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "received_by": forms.TextInput(attrs={"class": "form-control", "placeholder": "Receiver name"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }