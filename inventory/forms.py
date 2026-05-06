from django import forms
from django.core.exceptions import ValidationError

from .models import InventoryCategory, InventoryItem, StockIn, StockOut, Supplier


class InventoryCategoryForm(forms.ModelForm):
    class Meta:
        model = InventoryCategory
        fields = ["name", "description", "is_active"]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Stationery, Cleaning, Electronics"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "phone", "email", "contact_person", "address", "is_active"]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Supplier name"
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Phone number"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Email address"
            }),
            "contact_person": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Contact person"
            }),
            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }


class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = [
            "name",
            "item_code",
            "category",
            "supplier",
            "unit",
            "quantity",
            "reorder_level",
            "buying_price",
            "location",
            "status",
            "description",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Item name"
            }),
            "item_code": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: INV-001"
            }),
            "category": forms.Select(attrs={
                "class": "form-select"
            }),
            "supplier": forms.Select(attrs={
                "class": "form-select"
            }),
            "unit": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "pcs, box, litre, kg"
            }),
            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0
            }),
            "reorder_level": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0
            }),
            "buying_price": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0
            }),
            "location": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Store room / shelf"
            }),
            "status": forms.Select(attrs={
                "class": "form-select"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),
        }


class StockInForm(forms.ModelForm):
    class Meta:
        model = StockIn
        fields = [
            "item",
            "quantity",
            "supplier",
            "buying_price",
            "received_date",
            "reference",
            "notes",
        ]

        widgets = {
            "item": forms.Select(attrs={
                "class": "form-select"
            }),
            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1
            }),
            "supplier": forms.Select(attrs={
                "class": "form-select"
            }),
            "buying_price": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0
            }),
            "received_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "reference": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Invoice / receipt reference"
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),
        }


class StockOutForm(forms.ModelForm):
    class Meta:
        model = StockOut
        fields = [
            "item",
            "quantity",
            "purpose",
            "issued_to",
            "issued_date",
            "reference",
            "notes",
        ]

        widgets = {
            "item": forms.Select(attrs={
                "class": "form-select"
            }),
            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1
            }),
            "purpose": forms.Select(attrs={
                "class": "form-select"
            }),
            "issued_to": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Person / department"
            }),
            "issued_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "reference": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Reference"
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),
        }

    def clean(self):
        cleaned_data = super().clean()

        item = cleaned_data.get("item")
        quantity = cleaned_data.get("quantity")

        if item and quantity:
            if quantity > item.quantity:
                raise ValidationError(
                    f"Insufficient stock. Available quantity is {item.quantity} {item.unit}."
                )

        return cleaned_data