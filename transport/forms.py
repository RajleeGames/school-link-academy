from django import forms

from .models import Driver, StudentTransportAssignment, TransportRoute, TripLog, Vehicle


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ["vehicle_name", "plate_number", "vehicle_type", "capacity", "status", "notes"]

        widgets = {
            "vehicle_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Example: School Bus 1"}),
            "plate_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Example: T123ABC"}),
            "vehicle_type": forms.TextInput(attrs={"class": "form-control", "placeholder": "Bus / Van / Coaster"}),
            "capacity": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ["full_name", "phone", "license_number", "address", "status"]

        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Driver full name"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone number"}),
            "license_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "License number"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "status": forms.Select(attrs={"class": "form-select"}),
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
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Example: Moshi Town Route"}),
            "pickup_area": forms.TextInput(attrs={"class": "form-control", "placeholder": "Pickup area"}),
            "dropoff_area": forms.TextInput(attrs={"class": "form-control", "placeholder": "Dropoff area"}),
            "monthly_fee": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0}),
            "vehicle": forms.Select(attrs={"class": "form-select"}),
            "driver": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


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
            "student": forms.Select(attrs={"class": "form-select"}),
            "route": forms.Select(attrs={"class": "form-select"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "pickup_point": forms.TextInput(attrs={"class": "form-control", "placeholder": "Student pickup point"}),
            "guardian_phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Guardian phone"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


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
            "route": forms.Select(attrs={"class": "form-select"}),
            "vehicle": forms.Select(attrs={"class": "form-select"}),
            "driver": forms.Select(attrs={"class": "form-select"}),
            "trip_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "trip_type": forms.Select(attrs={"class": "form-select"}),
            "students_count": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "remarks": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }