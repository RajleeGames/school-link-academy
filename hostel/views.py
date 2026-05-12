from django.contrib import messages
from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import permission_required

from audit.utils import log_audit, model_to_dict_safe

from .forms import (
    BoardingAllocationForm,
    BoardingCheckoutForm,
    HostelBedForm,
    HostelForm,
    HostelRoomForm,
)
from .models import BoardingAllocation, Hostel, HostelBed, HostelRoom


def safe_delete_object(request, obj, success_message, redirect_url):
    old_values = model_to_dict_safe(obj)
    app_label = obj._meta.app_label
    model_name = obj._meta.model_name
    object_id = str(obj.pk)
    object_repr = str(obj)

    try:
        obj.delete()

        log_audit(
            request,
            "delete",
            app_label=app_label,
            model_name=model_name,
            object_id=object_id,
            object_repr=object_repr,
            message=f"Deleted {model_name}: {object_repr}",
            old_values=old_values,
        )

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


def release_allocation_bed(allocation):
    bed = allocation.bed

    if allocation.status == "active":
        bed.status = "available"
        bed.save()


@permission_required("hostel.view")
def hostel_home(request):
    total_hostels = Hostel.objects.count()
    total_rooms = HostelRoom.objects.count()
    total_beds = HostelBed.objects.count()
    available_beds = HostelBed.objects.filter(status="available").count()
    occupied_beds = HostelBed.objects.filter(status="occupied").count()
    active_allocations = BoardingAllocation.objects.filter(status="active").count()

    recent_allocations = BoardingAllocation.objects.select_related(
        "student",
        "bed",
        "bed__room",
        "bed__room__hostel",
    ).order_by("-id")[:8]

    hostels = Hostel.objects.annotate(
        room_count=Count("rooms"),
        bed_count=Count("rooms__beds"),
    )

    context = {
        "total_hostels": total_hostels,
        "total_rooms": total_rooms,
        "total_beds": total_beds,
        "available_beds": available_beds,
        "occupied_beds": occupied_beds,
        "active_allocations": active_allocations,
        "recent_allocations": recent_allocations,
        "hostels": hostels,
    }

    return render(request, "hostel/home.html", context)


@permission_required("hostel.view")
def hostel_list(request):
    hostels = Hostel.objects.annotate(
        room_count=Count("rooms"),
        bed_count=Count("rooms__beds"),
    )

    search = request.GET.get("search", "").strip()

    if search:
        hostels = hostels.filter(
            Q(name__icontains=search) |
            Q(location__icontains=search)
        )

    return render(request, "hostel/hostel_list.html", {
        "hostels": hostels,
        "search": search,
    })


@permission_required("hostel.manage")
def hostel_create(request):
    if request.method == "POST":
        form = HostelForm(request.POST)

        if form.is_valid():
            hostel = form.save()

            log_audit(
                request,
                "create",
                obj=hostel,
                message=f"Created hostel: {hostel}",
                new_values=model_to_dict_safe(hostel),
            )

            messages.success(request, "Hostel added successfully.")
            return redirect("hostel_list")

        messages.error(request, "Please correct the hostel form.")

    else:
        form = HostelForm()

    return render(request, "hostel/simple_form.html", {
        "form": form,
        "title": "Add Hostel",
        "button_text": "Save Hostel",
        "back_url": "hostel_list",
    })


@permission_required("hostel.manage")
def hostel_update(request, pk):
    hostel = get_object_or_404(Hostel, pk=pk)
    old_values = model_to_dict_safe(hostel)

    if request.method == "POST":
        form = HostelForm(request.POST, instance=hostel)

        if form.is_valid():
            updated_hostel = form.save()

            log_audit(
                request,
                "update",
                obj=updated_hostel,
                message=f"Updated hostel: {updated_hostel}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_hostel),
            )

            messages.success(request, "Hostel updated successfully.")
            return redirect("hostel_list")

        messages.error(request, "Please correct the hostel form.")

    else:
        form = HostelForm(instance=hostel)

    return render(request, "hostel/simple_form.html", {
        "form": form,
        "title": "Edit Hostel",
        "button_text": "Update Hostel",
        "back_url": "hostel_list",
    })


@permission_required("hostel.manage")
def hostel_delete(request, pk):
    hostel = get_object_or_404(Hostel, pk=pk)

    if hostel.rooms.exists():
        messages.error(
            request,
            "This hostel has rooms. Delete/move rooms first, or mark the hostel inactive instead."
        )
        return redirect("hostel_list")

    if request.method == "POST":
        return safe_delete_object(
            request,
            hostel,
            "Hostel deleted successfully.",
            "hostel_list"
        )

    return redirect("hostel_list")


@permission_required("hostel.view")
def room_list(request):
    rooms = HostelRoom.objects.select_related("hostel").annotate(
        bed_count=Count("beds")
    )

    search = request.GET.get("search", "").strip()
    hostel_id = request.GET.get("hostel", "").strip()

    if search:
        rooms = rooms.filter(
            Q(room_number__icontains=search) |
            Q(hostel__name__icontains=search)
        )

    if hostel_id:
        rooms = rooms.filter(hostel_id=hostel_id)

    return render(request, "hostel/room_list.html", {
        "rooms": rooms,
        "hostels": Hostel.objects.filter(is_active=True),
        "search": search,
        "selected_hostel": hostel_id,
    })


@permission_required("hostel.manage")
def room_create(request):
    if request.method == "POST":
        form = HostelRoomForm(request.POST)

        if form.is_valid():
            room = form.save()

            log_audit(
                request,
                "create",
                obj=room,
                message=f"Created hostel room: {room}",
                new_values=model_to_dict_safe(room),
            )

            messages.success(request, "Room added successfully.")
            return redirect("hostel_room_list")

        messages.error(request, "Please correct the room form.")

    else:
        form = HostelRoomForm()

    return render(request, "hostel/simple_form.html", {
        "form": form,
        "title": "Add Room",
        "button_text": "Save Room",
        "back_url": "hostel_room_list",
    })


@permission_required("hostel.manage")
def room_update(request, pk):
    room = get_object_or_404(HostelRoom, pk=pk)
    old_values = model_to_dict_safe(room)

    if request.method == "POST":
        form = HostelRoomForm(request.POST, instance=room)

        if form.is_valid():
            updated_room = form.save()

            log_audit(
                request,
                "update",
                obj=updated_room,
                message=f"Updated hostel room: {updated_room}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_room),
            )

            messages.success(request, "Room updated successfully.")
            return redirect("hostel_room_list")

        messages.error(request, "Please correct the room form.")

    else:
        form = HostelRoomForm(instance=room)

    return render(request, "hostel/simple_form.html", {
        "form": form,
        "title": "Edit Room",
        "button_text": "Update Room",
        "back_url": "hostel_room_list",
    })


@permission_required("hostel.manage")
def room_delete(request, pk):
    room = get_object_or_404(HostelRoom, pk=pk)

    if room.beds.exists():
        messages.error(
            request,
            "This room has beds. Delete/move beds first, or mark the room inactive instead."
        )
        return redirect("hostel_room_list")

    if request.method == "POST":
        return safe_delete_object(
            request,
            room,
            "Room deleted successfully.",
            "hostel_room_list"
        )

    return redirect("hostel_room_list")


@permission_required("hostel.view")
def bed_list(request):
    beds = HostelBed.objects.select_related("room", "room__hostel")

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        beds = beds.filter(
            Q(bed_number__icontains=search) |
            Q(room__room_number__icontains=search) |
            Q(room__hostel__name__icontains=search)
        )

    if status:
        beds = beds.filter(status=status)

    return render(request, "hostel/bed_list.html", {
        "beds": beds,
        "search": search,
        "selected_status": status,
    })


@permission_required("hostel.manage")
def bed_create(request):
    if request.method == "POST":
        form = HostelBedForm(request.POST)

        if form.is_valid():
            bed = form.save()

            log_audit(
                request,
                "create",
                obj=bed,
                message=f"Created hostel bed: {bed}",
                new_values=model_to_dict_safe(bed),
            )

            messages.success(request, "Bed added successfully.")
            return redirect("hostel_bed_list")

        messages.error(request, "Please correct the bed form.")

    else:
        form = HostelBedForm()

    return render(request, "hostel/simple_form.html", {
        "form": form,
        "title": "Add Bed",
        "button_text": "Save Bed",
        "back_url": "hostel_bed_list",
    })


@permission_required("hostel.manage")
def bed_update(request, pk):
    bed = get_object_or_404(HostelBed, pk=pk)
    old_values = model_to_dict_safe(bed)

    if request.method == "POST":
        form = HostelBedForm(request.POST, instance=bed)

        if form.is_valid():
            updated_bed = form.save()

            log_audit(
                request,
                "update",
                obj=updated_bed,
                message=f"Updated hostel bed: {updated_bed}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_bed),
            )

            messages.success(request, "Bed updated successfully.")
            return redirect("hostel_bed_list")

        messages.error(request, "Please correct the bed form.")

    else:
        form = HostelBedForm(instance=bed)

    return render(request, "hostel/simple_form.html", {
        "form": form,
        "title": "Edit Bed",
        "button_text": "Update Bed",
        "back_url": "hostel_bed_list",
    })


@permission_required("hostel.manage")
def bed_delete(request, pk):
    bed = get_object_or_404(HostelBed, pk=pk)

    if BoardingAllocation.objects.filter(bed=bed).exists():
        messages.error(
            request,
            "This bed has allocation history. Do not delete it. Change its status to damaged/reserved/inactive instead."
        )
        return redirect("hostel_bed_list")

    if request.method == "POST":
        return safe_delete_object(
            request,
            bed,
            "Bed deleted successfully.",
            "hostel_bed_list"
        )

    return redirect("hostel_bed_list")


@permission_required("hostel.view")
def allocation_list(request):
    allocations = BoardingAllocation.objects.select_related(
        "student",
        "bed",
        "bed__room",
        "bed__room__hostel",
    )

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        allocations = allocations.filter(
            Q(student__admission_number__icontains=search) |
            Q(student__first_name__icontains=search) |
            Q(student__middle_name__icontains=search) |
            Q(student__last_name__icontains=search) |
            Q(bed__bed_number__icontains=search) |
            Q(bed__room__room_number__icontains=search) |
            Q(bed__room__hostel__name__icontains=search)
        )

    if status:
        allocations = allocations.filter(status=status)

    return render(request, "hostel/allocation_list.html", {
        "allocations": allocations,
        "search": search,
        "selected_status": status,
    })


@permission_required("hostel.manage")
def allocation_create(request):
    if request.method == "POST":
        form = BoardingAllocationForm(request.POST)

        if form.is_valid():
            allocation = form.save(commit=False)

            if allocation.bed.status != "available":
                messages.error(request, "This bed is not available for allocation.")
                return render(request, "hostel/simple_form.html", {
                    "form": form,
                    "title": "Allocate Student",
                    "button_text": "Save Allocation",
                    "back_url": "boarding_allocation_list",
                })

            allocation.status = "active"
            allocation.save()

            bed = allocation.bed
            old_bed_values = model_to_dict_safe(bed)

            bed.status = "occupied"
            bed.save()

            log_audit(
                request,
                "create",
                obj=allocation,
                message=f"Created boarding allocation and occupied bed: {bed}",
                new_values=model_to_dict_safe(allocation),
            )

            log_audit(
                request,
                "update",
                obj=bed,
                message=f"Bed marked as occupied after allocation: {bed}",
                old_values=old_bed_values,
                new_values=model_to_dict_safe(bed),
            )

            messages.success(request, "Student allocated to hostel successfully.")
            return redirect("boarding_allocation_detail", pk=allocation.pk)

        messages.error(request, "Please correct the allocation form.")

    else:
        form = BoardingAllocationForm()

    return render(request, "hostel/simple_form.html", {
        "form": form,
        "title": "Allocate Student",
        "button_text": "Save Allocation",
        "back_url": "boarding_allocation_list",
    })


@permission_required("hostel.view")
def allocation_detail(request, pk):
    allocation = get_object_or_404(
        BoardingAllocation.objects.select_related(
            "student",
            "bed",
            "bed__room",
            "bed__room__hostel",
        ),
        pk=pk
    )

    return render(request, "hostel/allocation_detail.html", {
        "allocation": allocation,
    })


@permission_required("hostel.manage")
def allocation_checkout(request, pk):
    allocation = get_object_or_404(
        BoardingAllocation.objects.select_related("bed"),
        pk=pk
    )

    old_status = allocation.status
    old_allocation_values = model_to_dict_safe(allocation)

    if request.method == "POST":
        form = BoardingCheckoutForm(request.POST, instance=allocation)

        if form.is_valid():
            updated = form.save(commit=False)

            if updated.status == "checked_out" and not updated.check_out_date:
                updated.check_out_date = timezone.localdate()

            updated.save()

            log_audit(
                request,
                "update",
                obj=updated,
                message=f"Updated boarding allocation status from {old_status} to {updated.status}: {updated}",
                old_values=old_allocation_values,
                new_values=model_to_dict_safe(updated),
            )

            if old_status == "active" and updated.status in ["checked_out", "cancelled"]:
                bed = updated.bed
                old_bed_values = model_to_dict_safe(bed)

                bed.status = "available"
                bed.save()

                log_audit(
                    request,
                    "update",
                    obj=bed,
                    message=f"Bed released after allocation status changed to {updated.status}: {bed}",
                    old_values=old_bed_values,
                    new_values=model_to_dict_safe(bed),
                )

            if old_status in ["checked_out", "cancelled"] and updated.status == "active":
                bed = updated.bed

                if bed.status != "available":
                    messages.error(request, "This bed is not available. Choose another bed or make it available first.")
                    return render(request, "hostel/simple_form.html", {
                        "form": form,
                        "title": "Checkout / Update Allocation",
                        "button_text": "Update Allocation",
                        "back_url": "boarding_allocation_list",
                    })

                old_bed_values = model_to_dict_safe(bed)

                bed.status = "occupied"
                bed.save()

                log_audit(
                    request,
                    "update",
                    obj=bed,
                    message=f"Bed marked as occupied after allocation re-activated: {bed}",
                    old_values=old_bed_values,
                    new_values=model_to_dict_safe(bed),
                )

            messages.success(request, "Boarding allocation updated successfully.")
            return redirect("boarding_allocation_detail", pk=allocation.pk)

        messages.error(request, "Please correct the checkout form.")

    else:
        form = BoardingCheckoutForm(instance=allocation)

    return render(request, "hostel/simple_form.html", {
        "form": form,
        "title": "Checkout / Update Allocation",
        "button_text": "Update Allocation",
        "back_url": "boarding_allocation_list",
    })


@permission_required("hostel.manage")
def allocation_delete(request, pk):
    allocation = get_object_or_404(
        BoardingAllocation.objects.select_related("bed"),
        pk=pk
    )

    old_allocation_values = model_to_dict_safe(allocation)
    app_label = allocation._meta.app_label
    model_name = allocation._meta.model_name
    object_id = str(allocation.pk)
    object_repr = str(allocation)

    if request.method == "POST":
        bed = allocation.bed
        old_bed_values = model_to_dict_safe(bed)

        release_allocation_bed(allocation)

        if allocation.status == "active":
            bed.refresh_from_db()

            log_audit(
                request,
                "update",
                obj=bed,
                message=f"Bed released after deleting active allocation: {bed}",
                old_values=old_bed_values,
                new_values=model_to_dict_safe(bed),
            )

        allocation.delete()

        log_audit(
            request,
            "delete",
            app_label=app_label,
            model_name=model_name,
            object_id=object_id,
            object_repr=object_repr,
            message=f"Deleted boarding allocation: {object_repr}",
            old_values=old_allocation_values,
        )

        messages.success(request, "Boarding allocation deleted successfully.")
        return redirect("boarding_allocation_list")

    return redirect("boarding_allocation_list")