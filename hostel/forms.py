from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Hostel, HostelRoom, HostelBed, BoardingAllocation


class HostelForm(forms.ModelForm):
    class Meta:
        model = Hostel
        fields = [
            "name",
            "location",
            "description",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Boys Hostel / Girls Hostel",
            }),
            "location": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Block A",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }


class HostelRoomForm(forms.ModelForm):
    class Meta:
        model = HostelRoom
        fields = [
            "hostel",
            "room_number",
            "room_type",
            "capacity",
            "is_active",
        ]

        widgets = {
            # Normal because hostels are usually few.
            "hostel": forms.Select(attrs={
                "class": "form-select",
            }),
            "room_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: A01",
            }),
            "room_type": forms.Select(attrs={
                "class": "form-select",
            }),
            "capacity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "hostel" in self.fields:
            self.fields["hostel"].empty_label = "Select hostel"


class HostelBedForm(forms.ModelForm):
    class Meta:
        model = HostelBed
        fields = [
            "room",
            "bed_number",
            "status",
            "notes",
        ]

        widgets = {
            # Searchable because rooms can become many.
            "room": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search room...",
            }),
            "bed_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: B1",
            }),
            "status": forms.Select(attrs={
                "class": "form-select",
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "room" in self.fields:
            self.fields["room"].empty_label = "Search / select room"


class BoardingAllocationForm(forms.ModelForm):
    class Meta:
        model = BoardingAllocation
        fields = [
            "student",
            "bed",
            "check_in_date",
            "guardian_contact",
            "notes",
        ]

        widgets = {
            # Searchable because students can become many.
            "student": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search student by name or admission number...",
            }),

            # Searchable because beds can become many.
            "bed": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search available bed...",
            }),

            "check_in_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "guardian_contact": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Guardian phone if needed",
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["bed"].queryset = HostelBed.objects.select_related(
            "room",
            "room__hostel",
        ).filter(status="available")

        if "student" in self.fields:
            self.fields["student"].empty_label = "Search / select student"

        if "bed" in self.fields:
            self.fields["bed"].empty_label = "Search / select available bed"

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get("student")
        bed = cleaned_data.get("bed")

        if student:
            existing = BoardingAllocation.objects.filter(
                student=student,
                status="active",
            )

            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise ValidationError(
                    "This student already has an active hostel allocation."
                )

        if bed and bed.status != "available":
            raise ValidationError("This bed is not available.")

        return cleaned_data


class BoardingCheckoutForm(forms.ModelForm):
    class Meta:
        model = BoardingAllocation
        fields = [
            "check_out_date",
            "status",
            "notes",
        ]

        widgets = {
            "check_out_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "status": forms.Select(attrs={
                "class": "form-select",
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        check_out_date = cleaned_data.get("check_out_date")
        status = cleaned_data.get("status")

        if status == "checked_out" and not check_out_date:
            cleaned_data["check_out_date"] = timezone.localdate()

        return cleaned_data