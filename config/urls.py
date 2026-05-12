from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),

   path("", include("accounts.urls")),

    path("", include("dashboard.urls")),

    path("school/", include("schools.urls")),
    path("academics/", include("academics.urls")),
    path("students/", include("students.urls")),
    path("staff/", include("staff.urls")),
    path("attendance/", include("attendance.urls")),
    path("fees/", include("fees.urls")),
    path("expenses/", include("expenses.urls")),
    path("reports/", include("reports.urls")),
    path("exams/", include("exams.urls")),
    path("audit/", include("audit.urls")),
    path("timetable/", include("timetable.urls")),
    path("homework/", include("homework.urls")),
    path("discipline/", include("discipline.urls")),
    path("library/", include("library.urls")),
    path("hostel/", include("hostel.urls")),
    path("transport/", include("transport.urls")),
    path("inventory/", include("inventory.urls")),
    path("payroll/", include("payroll.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)