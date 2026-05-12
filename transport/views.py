from django.contrib import messages
from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import permission_required

from audit.utils import log_audit, model_to_dict_safe

from .forms import (
    DriverForm,
    StudentTransportAssignmentForm,
    TransportRouteForm,
    TripLogForm,
    VehicleForm,
)
from .models import Driver, StudentTransportAssignment, TransportRoute, TripLog, Vehicle


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
            new_values={},
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


@permission_required("transport.view")
def transport_home(request):
    total_vehicles = Vehicle.objects.count()
    active_vehicles = Vehicle.objects.filter(status="active").count()
    total_drivers = Driver.objects.count()
    total_routes = TransportRoute.objects.count()
    active_assignments = StudentTransportAssignment.objects.filter(status="active").count()

    recent_assignments = StudentTransportAssignment.objects.select_related(
        "student",
        "route",
    ).order_by("-id")[:8]

    routes = TransportRoute.objects.annotate(
        student_count=Count("student_assignments")
    ).select_related("vehicle", "driver")[:8]

    return render(request, "transport/home.html", {
        "total_vehicles": total_vehicles,
        "active_vehicles": active_vehicles,
        "total_drivers": total_drivers,
        "total_routes": total_routes,
        "active_assignments": active_assignments,
        "recent_assignments": recent_assignments,
        "routes": routes,
    })


@permission_required("transport.view")
def vehicle_list(request):
    vehicles = Vehicle.objects.all()
    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        vehicles = vehicles.filter(
            Q(vehicle_name__icontains=search)
            | Q(plate_number__icontains=search)
            | Q(vehicle_type__icontains=search)
        )

    if status:
        vehicles = vehicles.filter(status=status)

    return render(request, "transport/vehicle_list.html", {
        "vehicles": vehicles,
        "search": search,
        "selected_status": status,
    })


@permission_required("transport.manage")
def vehicle_create(request):
    if request.method == "POST":
        form = VehicleForm(request.POST)

        if form.is_valid():
            vehicle = form.save()

            log_audit(
                request,
                "create",
                obj=vehicle,
                message=f"Created vehicle: {vehicle}",
                old_values={},
                new_values=model_to_dict_safe(vehicle),
            )

            messages.success(request, "Vehicle added successfully.")
            return redirect("vehicle_list")

        messages.error(request, "Please correct the vehicle form.")

    else:
        form = VehicleForm()

    return render(request, "transport/simple_form.html", {
        "form": form,
        "title": "Add Vehicle",
        "button_text": "Save Vehicle",
        "back_url": "vehicle_list",
    })


@permission_required("transport.manage")
def vehicle_update(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    old_values = model_to_dict_safe(vehicle)

    if request.method == "POST":
        form = VehicleForm(request.POST, instance=vehicle)

        if form.is_valid():
            updated_vehicle = form.save()

            log_audit(
                request,
                "update",
                obj=updated_vehicle,
                message=f"Updated vehicle: {updated_vehicle}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_vehicle),
            )

            messages.success(request, "Vehicle updated successfully.")
            return redirect("vehicle_list")

        messages.error(request, "Please correct the vehicle form.")

    else:
        form = VehicleForm(instance=vehicle)

    return render(request, "transport/simple_form.html", {
        "form": form,
        "title": "Edit Vehicle",
        "button_text": "Update Vehicle",
        "back_url": "vehicle_list",
    })


@permission_required("transport.manage")
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)

    if TransportRoute.objects.filter(vehicle=vehicle).exists() or TripLog.objects.filter(vehicle=vehicle).exists():
        messages.error(
            request,
            "This vehicle is already used in routes or trip logs. Mark it inactive or maintenance instead."
        )
        return redirect("vehicle_list")

    if request.method == "POST":
        return safe_delete_object(
            request,
            vehicle,
            "Vehicle deleted successfully.",
            "vehicle_list"
        )

    return redirect("vehicle_list")


@permission_required("transport.view")
def driver_list(request):
    drivers = Driver.objects.all()
    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        drivers = drivers.filter(
            Q(full_name__icontains=search)
            | Q(phone__icontains=search)
            | Q(license_number__icontains=search)
        )

    if status:
        drivers = drivers.filter(status=status)

    return render(request, "transport/driver_list.html", {
        "drivers": drivers,
        "search": search,
        "selected_status": status,
    })


@permission_required("transport.manage")
def driver_create(request):
    if request.method == "POST":
        form = DriverForm(request.POST)

        if form.is_valid():
            driver = form.save()

            log_audit(
                request,
                "create",
                obj=driver,
                message=f"Created driver: {driver}",
                old_values={},
                new_values=model_to_dict_safe(driver),
            )

            messages.success(request, "Driver added successfully.")
            return redirect("driver_list")

        messages.error(request, "Please correct the driver form.")

    else:
        form = DriverForm()

    return render(request, "transport/simple_form.html", {
        "form": form,
        "title": "Add Driver",
        "button_text": "Save Driver",
        "back_url": "driver_list",
    })


@permission_required("transport.manage")
def driver_update(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    old_values = model_to_dict_safe(driver)

    if request.method == "POST":
        form = DriverForm(request.POST, instance=driver)

        if form.is_valid():
            updated_driver = form.save()

            log_audit(
                request,
                "update",
                obj=updated_driver,
                message=f"Updated driver: {updated_driver}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_driver),
            )

            messages.success(request, "Driver updated successfully.")
            return redirect("driver_list")

        messages.error(request, "Please correct the driver form.")

    else:
        form = DriverForm(instance=driver)

    return render(request, "transport/simple_form.html", {
        "form": form,
        "title": "Edit Driver",
        "button_text": "Update Driver",
        "back_url": "driver_list",
    })


@permission_required("transport.manage")
def driver_delete(request, pk):
    driver = get_object_or_404(Driver, pk=pk)

    if TransportRoute.objects.filter(driver=driver).exists() or TripLog.objects.filter(driver=driver).exists():
        messages.error(
            request,
            "This driver is already used in routes or trip logs. Mark the driver inactive instead."
        )
        return redirect("driver_list")

    if request.method == "POST":
        return safe_delete_object(
            request,
            driver,
            "Driver deleted successfully.",
            "driver_list"
        )

    return redirect("driver_list")


@permission_required("transport.view")
def route_list(request):
    routes = TransportRoute.objects.select_related("vehicle", "driver").annotate(
        student_count=Count("student_assignments")
    )

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        routes = routes.filter(
            Q(name__icontains=search)
            | Q(pickup_area__icontains=search)
            | Q(dropoff_area__icontains=search)
            | Q(vehicle__plate_number__icontains=search)
            | Q(driver__full_name__icontains=search)
        )

    if status:
        routes = routes.filter(status=status)

    return render(request, "transport/route_list.html", {
        "routes": routes,
        "search": search,
        "selected_status": status,
    })


@permission_required("transport.manage")
def route_create(request):
    if request.method == "POST":
        form = TransportRouteForm(request.POST)

        if form.is_valid():
            route = form.save()

            log_audit(
                request,
                "create",
                obj=route,
                message=f"Created transport route: {route}",
                old_values={},
                new_values=model_to_dict_safe(route),
            )

            messages.success(request, "Route added successfully.")
            return redirect("transport_route_list")

        messages.error(request, "Please correct the route form.")

    else:
        form = TransportRouteForm()

    return render(request, "transport/simple_form.html", {
        "form": form,
        "title": "Add Route",
        "button_text": "Save Route",
        "back_url": "transport_route_list",
    })


@permission_required("transport.manage")
def route_update(request, pk):
    route = get_object_or_404(TransportRoute, pk=pk)
    old_values = model_to_dict_safe(route)

    if request.method == "POST":
        form = TransportRouteForm(request.POST, instance=route)

        if form.is_valid():
            updated_route = form.save()

            log_audit(
                request,
                "update",
                obj=updated_route,
                message=f"Updated transport route: {updated_route}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_route),
            )

            messages.success(request, "Route updated successfully.")
            return redirect("transport_route_list")

        messages.error(request, "Please correct the route form.")

    else:
        form = TransportRouteForm(instance=route)

    return render(request, "transport/simple_form.html", {
        "form": form,
        "title": "Edit Route",
        "button_text": "Update Route",
        "back_url": "transport_route_list",
    })


@permission_required("transport.manage")
def route_delete(request, pk):
    route = get_object_or_404(TransportRoute, pk=pk)

    if route.student_assignments.exists() or TripLog.objects.filter(route=route).exists():
        messages.error(
            request,
            "This route has student assignments or trip logs. Mark it inactive instead."
        )
        return redirect("transport_route_list")

    if request.method == "POST":
        return safe_delete_object(
            request,
            route,
            "Route deleted successfully.",
            "transport_route_list"
        )

    return redirect("transport_route_list")


@permission_required("transport.view")
def assignment_list(request):
    assignments = StudentTransportAssignment.objects.select_related(
        "student",
        "route"
    )

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        assignments = assignments.filter(
            Q(student__first_name__icontains=search)
            | Q(student__middle_name__icontains=search)
            | Q(student__last_name__icontains=search)
            | Q(student__admission_number__icontains=search)
            | Q(route__name__icontains=search)
            | Q(pickup_point__icontains=search)
        )

    if status:
        assignments = assignments.filter(status=status)

    return render(request, "transport/assignment_list.html", {
        "assignments": assignments,
        "search": search,
        "selected_status": status,
    })


@permission_required("transport.manage")
def assignment_create(request):
    if request.method == "POST":
        form = StudentTransportAssignmentForm(request.POST)

        if form.is_valid():
            assignment = form.save()

            log_audit(
                request,
                "create",
                obj=assignment,
                message=f"Created student transport assignment: {assignment}",
                old_values={},
                new_values=model_to_dict_safe(assignment),
            )

            messages.success(request, "Student transport assignment added successfully.")
            return redirect("transport_assignment_list")

        messages.error(request, "Please correct the assignment form.")

    else:
        form = StudentTransportAssignmentForm()

    return render(request, "transport/simple_form.html", {
        "form": form,
        "title": "Assign Student to Transport",
        "button_text": "Save Assignment",
        "back_url": "transport_assignment_list",
    })


@permission_required("transport.manage")
def assignment_update(request, pk):
    assignment = get_object_or_404(StudentTransportAssignment, pk=pk)
    old_values = model_to_dict_safe(assignment)

    if request.method == "POST":
        form = StudentTransportAssignmentForm(request.POST, instance=assignment)

        if form.is_valid():
            updated_assignment = form.save()

            log_audit(
                request,
                "update",
                obj=updated_assignment,
                message=f"Updated transport assignment: {updated_assignment}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_assignment),
            )

            messages.success(request, "Transport assignment updated successfully.")
            return redirect("transport_assignment_list")

        messages.error(request, "Please correct the assignment form.")

    else:
        form = StudentTransportAssignmentForm(instance=assignment)

    return render(request, "transport/simple_form.html", {
        "form": form,
        "title": "Edit Transport Assignment",
        "button_text": "Update Assignment",
        "back_url": "transport_assignment_list",
    })


@permission_required("transport.manage")
def assignment_delete(request, pk):
    assignment = get_object_or_404(StudentTransportAssignment, pk=pk)

    if request.method == "POST":
        return safe_delete_object(
            request,
            assignment,
            "Transport assignment deleted successfully.",
            "transport_assignment_list"
        )

    return redirect("transport_assignment_list")


@permission_required("transport.view")
def trip_log_list(request):
    trips = TripLog.objects.select_related("route", "vehicle", "driver")

    search = request.GET.get("search", "").strip()

    if search:
        trips = trips.filter(
            Q(route__name__icontains=search)
            | Q(vehicle__plate_number__icontains=search)
            | Q(driver__full_name__icontains=search)
        )

    return render(request, "transport/trip_log_list.html", {
        "trips": trips,
        "search": search,
    })


@permission_required("transport.manage")
def trip_log_create(request):
    if request.method == "POST":
        form = TripLogForm(request.POST)

        if form.is_valid():
            trip = form.save()

            log_audit(
                request,
                "create",
                obj=trip,
                message=f"Created trip log: {trip}",
                old_values={},
                new_values=model_to_dict_safe(trip),
            )

            messages.success(request, "Trip log added successfully.")
            return redirect("trip_log_list")

        messages.error(request, "Please correct the trip log form.")

    else:
        form = TripLogForm()

    return render(request, "transport/simple_form.html", {
        "form": form,
        "title": "Add Trip Log",
        "button_text": "Save Trip Log",
        "back_url": "trip_log_list",
    })


@permission_required("transport.manage")
def trip_log_update(request, pk):
    trip = get_object_or_404(TripLog, pk=pk)
    old_values = model_to_dict_safe(trip)

    if request.method == "POST":
        form = TripLogForm(request.POST, instance=trip)

        if form.is_valid():
            updated_trip = form.save()

            log_audit(
                request,
                "update",
                obj=updated_trip,
                message=f"Updated trip log: {updated_trip}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_trip),
            )

            messages.success(request, "Trip log updated successfully.")
            return redirect("trip_log_list")

        messages.error(request, "Please correct the trip log form.")

    else:
        form = TripLogForm(instance=trip)

    return render(request, "transport/simple_form.html", {
        "form": form,
        "title": "Edit Trip Log",
        "button_text": "Update Trip Log",
        "back_url": "trip_log_list",
    })


@permission_required("transport.manage")
def trip_log_delete(request, pk):
    trip = get_object_or_404(TripLog, pk=pk)

    if request.method == "POST":
        return safe_delete_object(
            request,
            trip,
            "Trip log deleted successfully.",
            "trip_log_list"
        )

    return redirect("trip_log_list")