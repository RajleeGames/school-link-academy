from django import forms

from .models import (
    Driver,
    StudentTransportAssignment,
    TransportRoute,
    TripLog,
    Vehicle,
)


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            "vehicle_name",
            "plate_number",
            "vehicle_type",
            "capacity",
            "status",
            "notes",
        ]

        widgets = {
            "vehicle_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: School Bus 1",
            }),
            "plate_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: T123ABC",
            }),
            "vehicle_type": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Bus / Van / Coaster",
            }),
            "capacity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
            }),
            "status": forms.Select(attrs={
                "class": "form-select",
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),
        }


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = [
            "full_name",
            "phone",
            "license_number",
            "address",
            "status",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Driver full name",
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Phone number",
            }),
            "license_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "License number",
            }),
            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),
            "status": forms.Select(attrs={
                "class": "form-select",
            }),
        }


class TransportRouteForm(forms.ModelForm):
    class Meta:
        model = TransportRoute
        fields = [
            "name",
            "pickup_area",
            "dropoff_area",
            "monthly_fee",
            "vehicle",
            "driver",
            "status",
            "notes",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Moshi Town Route",
            }),
            "pickup_area": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Pickup area",
            }),
            "dropoff_area": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Dropoff area",
            }),
            "monthly_fee": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0,
            }),

            # Searchable if the school has many vehicles/drivers.
            "vehicle": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search vehicle...",
            }),
            "driver": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search driver...",
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

        if "vehicle" in self.fields:
            self.fields["vehicle"].empty_label = "Search / select vehicle"

        if "driver" in self.fields:
            self.fields["driver"].empty_label = "Search / select driver"


class StudentTransportAssignmentForm(forms.ModelForm):
    class Meta:
        model = StudentTransportAssignment
        fields = [
            "student",
            "route",
            "start_date",
            "end_date",
            "pickup_point",
            "guardian_phone",
            "status",
            "notes",
        ]

        widgets = {
            # Searchable because students can be many.
            "student": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search student by name or admission number...",
            }),

            # Searchable if routes become many.
            "route": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search route...",
            }),

            "start_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "end_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "pickup_point": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Student pickup point",
            }),
            "guardian_phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Guardian phone",
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

        if "student" in self.fields:
            self.fields["student"].empty_label = "Search / select student"

        if "route" in self.fields:
            self.fields["route"].empty_label = "Search / select route"


class TripLogForm(forms.ModelForm):
    class Meta:
        model = TripLog
        fields = [
            "route",
            "vehicle",
            "driver",
            "trip_date",
            "trip_type",
            "students_count",
            "remarks",
        ]

        widgets = {
            # Searchable because these records can grow.
            "route": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search route...",
            }),
            "vehicle": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search vehicle...",
            }),
            "driver": forms.Select(attrs={
                "class": "form-select sl-search-select",
                "data-placeholder": "Search driver...",
            }),

            "trip_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "trip_type": forms.Select(attrs={
                "class": "form-select",
            }),
            "students_count": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
            }),
            "remarks": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "route" in self.fields:
            self.fields["route"].empty_label = "Search / select route"

        if "vehicle" in self.fields:
            self.fields["vehicle"].empty_label = "Search / select vehicle"

        if "driver" in self.fields:
            self.fields["driver"].empty_label = "Search / select driver"