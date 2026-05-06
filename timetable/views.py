from django.contrib import messages
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import permission_required

from academics.models import ClassLevel, Stream
from staff.models import StaffProfile

from .forms import RoomForm, TimeSlotForm, TimetableEntryForm
from .models import Room, TimeSlot, TimetableEntry


def safe_delete_object(request, obj, success_message, redirect_url):
    try:
        obj.delete()
        messages.success(request, success_message)
    except ProtectedError:
        messages.error(
            request,
            "This record cannot be deleted because it is already used somewhere. You can edit it or mark it inactive instead."
        )
    except Exception:
        messages.error(
            request,
            "This record could not be deleted. Please check if it is connected to other records."
        )

    return redirect(redirect_url)


@permission_required("timetable.view")
def timetable_home(request):
    total_rooms = Room.objects.count()
    total_slots = TimeSlot.objects.count()
    total_entries = TimetableEntry.objects.count()
    active_entries = TimetableEntry.objects.filter(is_active=True).count()

    recent_entries = TimetableEntry.objects.select_related(
        "class_level",
        "stream",
        "time_slot",
        "subject",
        "teacher",
        "room",
    ).order_by("-id")[:10]

    context = {
        "total_rooms": total_rooms,
        "total_slots": total_slots,
        "total_entries": total_entries,
        "active_entries": active_entries,
        "recent_entries": recent_entries,
    }

    return render(request, "timetable/home.html", context)


@permission_required("timetable.manage")
def room_list(request):
    rooms = Room.objects.all()

    if request.method == "POST":
        form = RoomForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Room saved successfully.")
            return redirect("room_list")

        messages.error(request, "Please correct the room form.")
    else:
        form = RoomForm()

    return render(request, "timetable/room_list.html", {
        "rooms": rooms,
        "form": form,
    })


@permission_required("timetable.manage")
def room_update(request, pk):
    room = get_object_or_404(Room, pk=pk)

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)

        if form.is_valid():
            form.save()
            messages.success(request, "Room updated successfully.")
            return redirect("room_list")

        messages.error(request, "Please correct the room form.")
    else:
        form = RoomForm(instance=room)

    return render(request, "timetable/simple_timetable_form.html", {
        "form": form,
        "title": "Update Room",
        "button_text": "Update Room",
        "back_url": "room_list",
    })


@permission_required("timetable.manage")
def room_delete(request, pk):
    room = get_object_or_404(Room, pk=pk)

    if request.method == "POST":
        return safe_delete_object(
            request,
            room,
            "Room deleted successfully.",
            "room_list"
        )

    return redirect("room_list")


@permission_required("timetable.manage")
def time_slot_list(request):
    slots = TimeSlot.objects.all()

    if request.method == "POST":
        form = TimeSlotForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Time slot saved successfully.")
            return redirect("time_slot_list")

        messages.error(request, "Please correct the time slot form.")
    else:
        form = TimeSlotForm()

    return render(request, "timetable/time_slot_list.html", {
        "slots": slots,
        "form": form,
    })


@permission_required("timetable.manage")
def time_slot_update(request, pk):
    slot = get_object_or_404(TimeSlot, pk=pk)

    if request.method == "POST":
        form = TimeSlotForm(request.POST, instance=slot)

        if form.is_valid():
            form.save()
            messages.success(request, "Time slot updated successfully.")
            return redirect("time_slot_list")

        messages.error(request, "Please correct the time slot form.")
    else:
        form = TimeSlotForm(instance=slot)

    return render(request, "timetable/simple_timetable_form.html", {
        "form": form,
        "title": "Update Time Slot",
        "button_text": "Update Time Slot",
        "back_url": "time_slot_list",
    })


@permission_required("timetable.manage")
def time_slot_delete(request, pk):
    slot = get_object_or_404(TimeSlot, pk=pk)

    if request.method == "POST":
        return safe_delete_object(
            request,
            slot,
            "Time slot deleted successfully.",
            "time_slot_list"
        )

    return redirect("time_slot_list")


@permission_required("timetable.manage")
def auto_create_default_time_slots(request):
    default_slots = [
        {"name": "Assembly", "start_time": "07:30", "end_time": "08:00", "is_break": False},
        {"name": "Period 1", "start_time": "08:00", "end_time": "08:40", "is_break": False},
        {"name": "Period 2", "start_time": "08:40", "end_time": "09:20", "is_break": False},
        {"name": "Short Break", "start_time": "09:20", "end_time": "09:40", "is_break": True},
        {"name": "Period 3", "start_time": "09:40", "end_time": "10:20", "is_break": False},
        {"name": "Period 4", "start_time": "10:20", "end_time": "11:00", "is_break": False},
        {"name": "Period 5", "start_time": "11:00", "end_time": "11:40", "is_break": False},
        {"name": "Lunch Break", "start_time": "11:40", "end_time": "12:30", "is_break": True},
        {"name": "Period 6", "start_time": "12:30", "end_time": "13:10", "is_break": False},
        {"name": "Period 7", "start_time": "13:10", "end_time": "13:50", "is_break": False},
        {"name": "Period 8", "start_time": "13:50", "end_time": "14:30", "is_break": False},
    ]

    created_count = 0
    updated_count = 0

    for slot_data in default_slots:
        slot, created = TimeSlot.objects.get_or_create(
            name=slot_data["name"],
            defaults={
                "start_time": slot_data["start_time"],
                "end_time": slot_data["end_time"],
                "is_break": slot_data["is_break"],
                "is_active": True,
            }
        )

        if created:
            created_count += 1
        else:
            slot.start_time = slot_data["start_time"]
            slot.end_time = slot_data["end_time"]
            slot.is_break = slot_data["is_break"]
            slot.is_active = True
            slot.save()
            updated_count += 1

    messages.success(
        request,
        f"Default time slots ready. Created {created_count}, updated {updated_count}."
    )

    return redirect("time_slot_list")


@permission_required("timetable.view")
def timetable_entry_list(request):
    query = request.GET.get("q", "").strip()
    class_filter = request.GET.get("class", "").strip()
    stream_filter = request.GET.get("stream", "").strip()
    day_filter = request.GET.get("day", "").strip()

    entries = TimetableEntry.objects.select_related(
        "class_level",
        "stream",
        "time_slot",
        "subject",
        "teacher",
        "room",
    ).all()

    if query:
        entries = entries.filter(
            Q(subject__name__icontains=query) |
            Q(teacher__first_name__icontains=query) |
            Q(teacher__middle_name__icontains=query) |
            Q(teacher__last_name__icontains=query) |
            Q(room__name__icontains=query) |
            Q(note__icontains=query)
        )

    if class_filter:
        entries = entries.filter(class_level_id=class_filter)

    if stream_filter:
        entries = entries.filter(stream_id=stream_filter)

    if day_filter:
        entries = entries.filter(day=day_filter)

    context = {
        "entries": entries,
        "query": query,
        "class_filter": class_filter,
        "stream_filter": stream_filter,
        "day_filter": day_filter,
        "classes": ClassLevel.objects.filter(is_active=True),
        "streams": Stream.objects.filter(is_active=True),
        "day_choices": TimetableEntry.DAY_CHOICES,
    }

    return render(request, "timetable/entry_list.html", context)


@permission_required("timetable.manage")
def timetable_entry_create(request):
    if request.method == "POST":
        form = TimetableEntryForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Timetable entry saved successfully.")
            return redirect("timetable_entry_list")

        messages.error(request, "Please correct the timetable form.")
    else:
        form = TimetableEntryForm()

    return render(request, "timetable/entry_form.html", {
        "form": form,
        "title": "Add Timetable Entry",
        "button_text": "Save Timetable Entry",
        "is_update": False,
    })


@permission_required("timetable.manage")
def timetable_entry_update(request, pk):
    entry = get_object_or_404(TimetableEntry, pk=pk)

    if request.method == "POST":
        form = TimetableEntryForm(request.POST, instance=entry)

        if form.is_valid():
            form.save()
            messages.success(request, "Timetable entry updated successfully.")
            return redirect("timetable_entry_list")

        messages.error(request, "Please correct the timetable form.")
    else:
        form = TimetableEntryForm(instance=entry)

    return render(request, "timetable/entry_form.html", {
        "form": form,
        "entry": entry,
        "title": "Update Timetable Entry",
        "button_text": "Update Timetable Entry",
        "is_update": True,
    })


@permission_required("timetable.manage")
def timetable_entry_delete(request, pk):
    entry = get_object_or_404(TimetableEntry, pk=pk)

    if request.method == "POST":
        entry.delete()
        messages.success(request, "Timetable entry deleted successfully.")

    return redirect("timetable_entry_list")


@permission_required("timetable.view")
def class_timetable(request):
    class_filter = request.GET.get("class", "").strip()
    stream_filter = request.GET.get("stream", "").strip()

    days = TimetableEntry.DAY_CHOICES
    slots = TimeSlot.objects.filter(is_active=True).order_by("start_time")

    entries = TimetableEntry.objects.select_related(
        "class_level",
        "stream",
        "time_slot",
        "subject",
        "teacher",
        "room",
    ).filter(is_active=True)

    selected_class = None
    selected_stream = None

    if class_filter:
        entries = entries.filter(class_level_id=class_filter)
        selected_class = ClassLevel.objects.filter(id=class_filter).first()

    if stream_filter:
        entries = entries.filter(stream_id=stream_filter)
        selected_stream = Stream.objects.filter(id=stream_filter).first()

    timetable_map = {}

    for entry in entries:
        timetable_map[(entry.day, entry.time_slot_id)] = entry

    table_rows = []

    for day_value, day_label in days:
        row = {
            "day_value": day_value,
            "day_label": day_label,
            "cells": [],
        }

        for slot in slots:
            row["cells"].append({
                "slot": slot,
                "entry": timetable_map.get((day_value, slot.id)),
            })

        table_rows.append(row)

    context = {
        "classes": ClassLevel.objects.filter(is_active=True),
        "streams": Stream.objects.filter(is_active=True),
        "class_filter": class_filter,
        "stream_filter": stream_filter,
        "selected_class": selected_class,
        "selected_stream": selected_stream,
        "slots": slots,
        "table_rows": table_rows,
    }

    return render(request, "timetable/class_timetable.html", context)


@permission_required("timetable.view")
def teacher_timetable(request):
    teacher_filter = request.GET.get("teacher", "").strip()

    days = TimetableEntry.DAY_CHOICES
    slots = TimeSlot.objects.filter(is_active=True).order_by("start_time")

    teachers = StaffProfile.objects.filter(role="teacher", status="active")

    entries = TimetableEntry.objects.select_related(
        "class_level",
        "stream",
        "time_slot",
        "subject",
        "teacher",
        "room",
    ).filter(is_active=True)

    selected_teacher = None

    if teacher_filter:
        entries = entries.filter(teacher_id=teacher_filter)
        selected_teacher = StaffProfile.objects.filter(id=teacher_filter).first()

    timetable_map = {}

    for entry in entries:
        timetable_map[(entry.day, entry.time_slot_id)] = entry

    table_rows = []

    for day_value, day_label in days:
        row = {
            "day_value": day_value,
            "day_label": day_label,
            "cells": [],
        }

        for slot in slots:
            row["cells"].append({
                "slot": slot,
                "entry": timetable_map.get((day_value, slot.id)),
            })

        table_rows.append(row)

    context = {
        "teachers": teachers,
        "teacher_filter": teacher_filter,
        "selected_teacher": selected_teacher,
        "slots": slots,
        "table_rows": table_rows,
    }

    return render(request, "timetable/teacher_timetable.html", context)