from datetime import date

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import permission_required
from accounts.permissions import user_has_permission
from audit.utils import log_audit, model_to_dict_safe

from academics.models import ClassLevel, Stream
from students.models import Student
from staff.models import StaffProfile

from .forms import StaffAttendanceForm, StudentAttendanceForm
from .models import StaffAttendance, StudentAttendance


# =====================================================
# AUDIT HELPERS
# =====================================================

def student_attendance_audit_message(record, prefix):
    return (
        f"{prefix} student attendance for {record.student.full_name} "
        f"on {record.date}"
    )


def staff_attendance_audit_message(record, prefix):
    return (
        f"{prefix} staff attendance for {record.staff.full_name} "
        f"on {record.date}"
    )


# =====================================================
# ATTENDANCE HOME
# =====================================================

@permission_required("attendance.view")
def attendance_home(request):
    today = date.today()

    can_manage_staff = user_has_permission(request.user, "attendance.manage_staff")

    student_total = Student.objects.filter(status="active").count()
    student_present = StudentAttendance.objects.filter(date=today, status="present").count()
    student_late = StudentAttendance.objects.filter(date=today, status="late").count()
    student_absent = StudentAttendance.objects.filter(date=today, status="absent").count()

    staff_total = 0
    staff_present = 0
    staff_late = 0
    staff_absent = 0
    recent_staff_attendance = []

    if can_manage_staff:
        staff_total = StaffProfile.objects.filter(status="active").count()
        staff_present = StaffAttendance.objects.filter(date=today, status="present").count()
        staff_late = StaffAttendance.objects.filter(date=today, status="late").count()
        staff_absent = StaffAttendance.objects.filter(date=today, status="absent").count()

        recent_staff_attendance = StaffAttendance.objects.select_related(
            "staff"
        ).order_by("-date", "-created_at")[:10]

    recent_student_attendance = StudentAttendance.objects.select_related(
        "student",
        "student__class_level",
        "student__stream",
    ).order_by("-date", "-created_at")[:10]

    context = {
        "today": today,
        "can_manage_staff": can_manage_staff,

        "student_total": student_total,
        "student_present": student_present,
        "student_late": student_late,
        "student_absent": student_absent,

        "staff_total": staff_total,
        "staff_present": staff_present,
        "staff_late": staff_late,
        "staff_absent": staff_absent,

        "recent_student_attendance": recent_student_attendance,
        "recent_staff_attendance": recent_staff_attendance,
    }

    return render(request, "attendance/home.html", context)


# =====================================================
# STUDENT ATTENDANCE
# =====================================================

@permission_required("attendance.view")
def student_attendance_list(request):
    query = request.GET.get("q", "").strip()
    date_filter = request.GET.get("date", "").strip()
    class_filter = request.GET.get("class", "").strip()
    status_filter = request.GET.get("status", "").strip()

    records = StudentAttendance.objects.select_related(
        "student",
        "student__class_level",
        "student__stream",
        "student__parent_guardian",
    ).all()

    if query:
        records = records.filter(
            Q(student__admission_number__icontains=query) |
            Q(student__first_name__icontains=query) |
            Q(student__middle_name__icontains=query) |
            Q(student__last_name__icontains=query)
        )

    if date_filter:
        records = records.filter(date=date_filter)

    if class_filter:
        records = records.filter(student__class_level_id=class_filter)

    if status_filter:
        records = records.filter(status=status_filter)

    context = {
        "records": records,
        "classes": ClassLevel.objects.filter(is_active=True),
        "query": query,
        "date_filter": date_filter,
        "class_filter": class_filter,
        "status_filter": status_filter,
        "status_choices": StudentAttendance.STATUS_CHOICES,
    }

    return render(request, "attendance/student_attendance_list.html", context)


@permission_required("attendance.manage_students")
def student_attendance_create(request):
    if request.method == "POST":
        form = StudentAttendanceForm(request.POST)

        if form.is_valid():
            record = form.save()

            log_audit(
                request,
                action="create",
                obj=record,
                message=student_attendance_audit_message(record, "Created"),
                old_values={},
                new_values=model_to_dict_safe(record),
            )

            messages.success(request, "Student attendance saved successfully.")
            return redirect("student_attendance_list")

        messages.error(request, "Please correct the student attendance form.")
    else:
        form = StudentAttendanceForm(initial={"date": date.today()})

    return render(request, "attendance/student_attendance_form.html", {
        "form": form,
        "title": "Mark Student Attendance",
        "button_text": "Save Attendance",
        "is_update": False,
    })


@permission_required("attendance.manage_students")
def student_attendance_update(request, pk):
    record = get_object_or_404(
        StudentAttendance.objects.select_related("student"),
        pk=pk
    )

    if request.method == "POST":
        old_values = model_to_dict_safe(record)
        form = StudentAttendanceForm(request.POST, instance=record)

        if form.is_valid():
            record = form.save()

            log_audit(
                request,
                action="update",
                obj=record,
                message=student_attendance_audit_message(record, "Updated"),
                old_values=old_values,
                new_values=model_to_dict_safe(record),
            )

            messages.success(request, "Student attendance updated successfully.")
            return redirect("student_attendance_list")

        messages.error(request, "Please correct the student attendance form.")
    else:
        form = StudentAttendanceForm(instance=record)

    return render(request, "attendance/student_attendance_form.html", {
        "form": form,
        "record": record,
        "title": "Update Student Attendance",
        "button_text": "Update Attendance",
        "is_update": True,
    })


@permission_required("attendance.manage_students")
def student_attendance_delete(request, pk):
    record = get_object_or_404(
        StudentAttendance.objects.select_related("student"),
        pk=pk
    )

    if request.method == "POST":
        old_values = model_to_dict_safe(record)

        log_audit(
            request,
            action="delete",
            obj=record,
            message=student_attendance_audit_message(record, "Deleted"),
            old_values=old_values,
            new_values={},
        )

        record.delete()
        messages.success(request, "Student attendance record deleted successfully.")

    return redirect("student_attendance_list")


@permission_required("attendance.manage_students")
def bulk_student_attendance(request):
    selected_date = request.GET.get("date") or request.POST.get("date") or date.today().isoformat()
    class_id = request.GET.get("class") or request.POST.get("class") or ""
    stream_id = request.GET.get("stream") or request.POST.get("stream") or ""

    classes = ClassLevel.objects.filter(is_active=True)
    streams = Stream.objects.select_related("class_level").filter(is_active=True)

    students = Student.objects.select_related(
        "class_level",
        "stream",
        "parent_guardian"
    ).filter(status="active")

    if class_id:
        students = students.filter(class_level_id=class_id)

    if stream_id:
        students = students.filter(stream_id=stream_id)

    students = students.order_by(
        "class_level__order",
        "stream__name",
        "first_name",
        "last_name"
    )

    existing_records = {
        record.student_id: record
        for record in StudentAttendance.objects.filter(date=selected_date)
    }

    if request.method == "POST":
        if not class_id:
            messages.error(request, "Please choose a class first.")
            return redirect("bulk_student_attendance")

        saved_count = 0
        created_count = 0
        updated_count = 0
        changed_students = []

        for student in students:
            status = request.POST.get(f"status_{student.id}", "present")
            arrival_time = request.POST.get(f"arrival_time_{student.id}") or None
            remarks = request.POST.get(f"remarks_{student.id}", "").strip()

            old_record = existing_records.get(student.id)
            old_values = model_to_dict_safe(old_record) if old_record else {}

            record, created = StudentAttendance.objects.update_or_create(
                student=student,
                date=selected_date,
                defaults={
                    "status": status,
                    "arrival_time": arrival_time,
                    "remarks": remarks,
                }
            )

            if created:
                created_count += 1
                audit_action = "create"
                audit_prefix = "Created by bulk entry"
            else:
                updated_count += 1
                audit_action = "update"
                audit_prefix = "Updated by bulk entry"

            log_audit(
                request,
                action=audit_action,
                obj=record,
                message=student_attendance_audit_message(record, audit_prefix),
                old_values=old_values,
                new_values=model_to_dict_safe(record),
            )

            changed_students.append(student.full_name)
            saved_count += 1

        log_audit(
            request,
            action="generate",
            obj=None,
            app_label="attendance",
            model_name="studentattendance",
            object_repr=f"Bulk Student Attendance {selected_date}",
            message=(
                f"Bulk student attendance saved for {saved_count} students "
                f"on {selected_date}. Created {created_count}, updated {updated_count}."
            ),
            old_values={},
            new_values={
                "date": selected_date,
                "class_id": class_id,
                "stream_id": stream_id,
                "saved_count": saved_count,
                "created_count": created_count,
                "updated_count": updated_count,
                "students": changed_students,
            },
        )

        messages.success(request, f"Attendance saved for {saved_count} students.")
        return redirect("student_attendance_list")

    context = {
        "classes": classes,
        "streams": streams,
        "students": students,
        "existing_records": existing_records,
        "selected_date": selected_date,
        "class_id": class_id,
        "stream_id": stream_id,
        "status_choices": StudentAttendance.STATUS_CHOICES,
    }

    return render(request, "attendance/bulk_student_attendance.html", context)


# =====================================================
# STAFF ATTENDANCE
# =====================================================

@permission_required("attendance.view")
def staff_attendance_list(request):
    if not user_has_permission(request.user, "attendance.manage_staff"):
        messages.error(request, "You are not allowed to view staff attendance.")
        return render(request, "accounts/access_denied.html", {
            "permission_code": "attendance.manage_staff",
        }, status=403)

    query = request.GET.get("q", "").strip()
    date_filter = request.GET.get("date", "").strip()
    status_filter = request.GET.get("status", "").strip()

    records = StaffAttendance.objects.select_related("staff").all()

    if query:
        records = records.filter(
            Q(staff__staff_id__icontains=query) |
            Q(staff__first_name__icontains=query) |
            Q(staff__middle_name__icontains=query) |
            Q(staff__last_name__icontains=query) |
            Q(staff__phone__icontains=query)
        )

    if date_filter:
        records = records.filter(date=date_filter)

    if status_filter:
        records = records.filter(status=status_filter)

    context = {
        "records": records,
        "query": query,
        "date_filter": date_filter,
        "status_filter": status_filter,
        "status_choices": StaffAttendance.STATUS_CHOICES,
    }

    return render(request, "attendance/staff_attendance_list.html", context)


@permission_required("attendance.manage_staff")
def staff_attendance_create(request):
    if request.method == "POST":
        form = StaffAttendanceForm(request.POST)

        if form.is_valid():
            record = form.save()

            log_audit(
                request,
                action="create",
                obj=record,
                message=staff_attendance_audit_message(record, "Created"),
                old_values={},
                new_values=model_to_dict_safe(record),
            )

            messages.success(request, "Staff attendance saved successfully.")
            return redirect("staff_attendance_list")

        messages.error(request, "Please correct the staff attendance form.")
    else:
        form = StaffAttendanceForm(initial={"date": date.today()})

    return render(request, "attendance/staff_attendance_form.html", {
        "form": form,
        "title": "Mark Staff Attendance",
        "button_text": "Save Attendance",
        "is_update": False,
    })


@permission_required("attendance.manage_staff")
def staff_attendance_update(request, pk):
    record = get_object_or_404(
        StaffAttendance.objects.select_related("staff"),
        pk=pk
    )

    if request.method == "POST":
        old_values = model_to_dict_safe(record)
        form = StaffAttendanceForm(request.POST, instance=record)

        if form.is_valid():
            record = form.save()

            log_audit(
                request,
                action="update",
                obj=record,
                message=staff_attendance_audit_message(record, "Updated"),
                old_values=old_values,
                new_values=model_to_dict_safe(record),
            )

            messages.success(request, "Staff attendance updated successfully.")
            return redirect("staff_attendance_list")

        messages.error(request, "Please correct the staff attendance form.")
    else:
        form = StaffAttendanceForm(instance=record)

    return render(request, "attendance/staff_attendance_form.html", {
        "form": form,
        "record": record,
        "title": "Update Staff Attendance",
        "button_text": "Update Attendance",
        "is_update": True,
    })


@permission_required("attendance.manage_staff")
def staff_attendance_delete(request, pk):
    record = get_object_or_404(
        StaffAttendance.objects.select_related("staff"),
        pk=pk
    )

    if request.method == "POST":
        old_values = model_to_dict_safe(record)

        log_audit(
            request,
            action="delete",
            obj=record,
            message=staff_attendance_audit_message(record, "Deleted"),
            old_values=old_values,
            new_values={},
        )

        record.delete()
        messages.success(request, "Staff attendance record deleted successfully.")

    return redirect("staff_attendance_list")


# =====================================================
# DAILY REGISTER
# =====================================================

@permission_required("attendance.view")
def daily_register(request):
    selected_date = request.GET.get("date", "").strip() or date.today().isoformat()
    class_id = request.GET.get("class", "").strip()
    stream_id = request.GET.get("stream", "").strip()
    student_status = request.GET.get("student_status", "").strip()
    staff_status = request.GET.get("staff_status", "").strip()

    can_manage_staff = user_has_permission(request.user, "attendance.manage_staff")

    classes = ClassLevel.objects.filter(is_active=True)
    streams = Stream.objects.select_related("class_level").filter(is_active=True)

    students = Student.objects.select_related(
        "class_level",
        "stream",
        "parent_guardian",
    ).filter(status="active")

    if class_id:
        students = students.filter(class_level_id=class_id)

    if stream_id:
        students = students.filter(stream_id=stream_id)

    students = students.order_by(
        "class_level__order",
        "stream__name",
        "first_name",
        "last_name"
    )

    student_attendance_map = {
        record.student_id: record
        for record in StudentAttendance.objects.select_related("student").filter(date=selected_date)
    }

    student_rows = []

    for student in students:
        attendance = student_attendance_map.get(student.id)

        if student_status:
            if student_status == "not_marked" and attendance:
                continue

            if student_status != "not_marked":
                if not attendance or attendance.status != student_status:
                    continue

        student_rows.append({
            "student": student,
            "attendance": attendance,
        })

    staff_rows = []
    staff_total = 0
    staff_marked_count = 0
    staff_not_marked_count = 0

    if can_manage_staff:
        staff_members = StaffProfile.objects.filter(status="active").order_by(
            "first_name",
            "last_name"
        )

        staff_attendance_map = {
            record.staff_id: record
            for record in StaffAttendance.objects.select_related("staff").filter(date=selected_date)
        }

        for staff in staff_members:
            attendance = staff_attendance_map.get(staff.id)

            if staff_status:
                if staff_status == "not_marked" and attendance:
                    continue

                if staff_status != "not_marked":
                    if not attendance or attendance.status != staff_status:
                        continue

            staff_rows.append({
                "staff": staff,
                "attendance": attendance,
            })

        staff_total = staff_members.count()
        staff_marked_count = len(staff_attendance_map)
        staff_not_marked_count = max(staff_total - staff_marked_count, 0)

    student_total = students.count()
    student_marked_count = len(student_attendance_map)
    student_not_marked_count = max(student_total - student_marked_count, 0)

    context = {
        "selected_date": selected_date,
        "can_manage_staff": can_manage_staff,

        "classes": classes,
        "streams": streams,
        "class_id": class_id,
        "stream_id": stream_id,

        "student_status": student_status,
        "staff_status": staff_status,

        "student_status_choices": StudentAttendance.STATUS_CHOICES,
        "staff_status_choices": StaffAttendance.STATUS_CHOICES,

        "student_rows": student_rows,
        "staff_rows": staff_rows,

        "student_total": student_total,
        "student_marked_count": student_marked_count,
        "student_not_marked_count": student_not_marked_count,

        "staff_total": staff_total,
        "staff_marked_count": staff_marked_count,
        "staff_not_marked_count": staff_not_marked_count,
    }

    return render(request, "attendance/daily_register.html", context)