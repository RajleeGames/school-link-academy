from django import forms
from .models import StudentInvoiceItem
from .models import (
    FeeCategory,
    FeeStructure,
    StudentInvoice,
    StudentInvoiceItem,
    FeePayment,
)


class FeeCategoryForm(forms.ModelForm):
    class Meta:
        model = FeeCategory
        fields = ["name", "description", "is_active"]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Tuition Fee",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
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
            "category": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search fee category...",
            }),
            "academic_year": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search academic year...",
            }),
            "term": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search term...",
            }),
            "class_level": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search class...",
            }),
            "amount": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
            }),
            "is_required": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "category" in self.fields:
            self.fields["category"].empty_label = "Search / select fee category"

        if "academic_year" in self.fields:
            self.fields["academic_year"].empty_label = "Search / select academic year"

        if "term" in self.fields:
            self.fields["term"].empty_label = "Search / select term"

        if "class_level" in self.fields:
            self.fields["class_level"].empty_label = "Search / select class"


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
            "student": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search student by name or admission number...",
            }),
            "academic_year": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search academic year...",
            }),
            "term": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search term...",
            }),
            "invoice_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: INV-0001",
            }),
            "total_amount": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
            }),
            "discount_amount": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
            }),
            "invoice_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "due_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "student" in self.fields:
            self.fields["student"].empty_label = "Search / select student"

        if "academic_year" in self.fields:
            self.fields["academic_year"].empty_label = "Search / select academic year"

        if "term" in self.fields:
            self.fields["term"].empty_label = "Search / select term"


class StudentInvoiceItemForm(forms.ModelForm):
    class Meta:
        model = StudentInvoiceItem
        fields = ["category", "description", "amount"]

        widgets = {
            "category": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search fee category...",
            }),
            "description": forms.TextInput(attrs={
                "class": "form-control",
            }),
            "amount": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "category" in self.fields:
            self.fields["category"].empty_label = "Search / select fee category"


class FeePaymentForm(forms.ModelForm):
    class Meta:
        model = FeePayment
        fields = [
            "invoice",
            "fee_item",
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
            "invoice": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search invoice by student, number, or balance...",
            }),
            "fee_item": forms.Select(attrs={
                "class": "form-select",
            }),
            "receipt_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: REC-0001",
            }),
            "payment_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "amount": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
            }),
            "method": forms.Select(attrs={
                "class": "form-select",
            }),
            "reference": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Transaction reference",
            }),
            "status": forms.Select(attrs={
                "class": "form-select",
            }),
            "received_by": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Receiver name",
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
            }),
        }

    def __init__(self, *args, **kwargs):
        invoice = kwargs.pop("invoice", None)
        super().__init__(*args, **kwargs)

        if "invoice" in self.fields:
            self.fields["invoice"].empty_label = "Search / select invoice"

        self.fields["fee_item"].required = False
        self.fields["fee_item"].empty_label = "General payment / choose fee item"

        if invoice:
            self.fields["fee_item"].queryset = StudentInvoiceItem.objects.filter(
                invoice=invoice
            ).select_related("category").order_by("category__name")
        elif self.instance and self.instance.pk and self.instance.invoice_id:
            self.fields["fee_item"].queryset = StudentInvoiceItem.objects.filter(
                invoice=self.instance.invoice
            ).select_related("category").order_by("category__name")
        else:
            self.fields["fee_item"].queryset = StudentInvoiceItem.objects.none()

    def clean(self):
        cleaned_data = super().clean()

        invoice = cleaned_data.get("invoice")
        fee_item = cleaned_data.get("fee_item")

        if invoice and fee_item and fee_item.invoice_id != invoice.id:
            raise forms.ValidationError(
                "Selected fee item does not belong to the selected invoice."
            )

        return cleaned_data