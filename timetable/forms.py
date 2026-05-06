from django import forms
from .models import Room, TimeSlot, TimetableEntry


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ["name", "description", "is_active"]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Room 1, Science Lab, Computer Lab"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Optional description"
            }),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ["name", "start_time", "end_time", "is_break", "is_active"]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Period 1, Break, Lunch"
            }),
            "start_time": forms.TimeInput(attrs={
                "class": "form-control",
                "type": "time"
            }),
            "end_time": forms.TimeInput(attrs={
                "class": "form-control",
                "type": "time"
            }),
            "is_break": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class TimetableEntryForm(forms.ModelForm):
    class Meta:
        model = TimetableEntry
        fields = [
            "class_level",
            "stream",
            "day",
            "time_slot",
            "subject",
            "teacher",
            "room",
            "note",
            "is_active",
        ]

        widgets = {
            "class_level": forms.Select(attrs={"class": "form-select"}),
            "stream": forms.Select(attrs={"class": "form-select"}),
            "day": forms.Select(attrs={"class": "form-select"}),
            "time_slot": forms.Select(attrs={"class": "form-select"}),
            "subject": forms.Select(attrs={"class": "form-select"}),
            "teacher": forms.Select(attrs={"class": "form-select"}),
            "room": forms.Select(attrs={"class": "form-select"}),
            "note": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Optional note"
            }),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }