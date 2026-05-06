from django.db import models


class SchoolProfile(models.Model):
    SCHOOL_TYPE_CHOICES = [
        ("primary", "Primary School"),
        ("secondary", "Secondary School"),
        ("both", "Primary & Secondary"),
    ]

    SCHOOL_MODE_CHOICES = [
        ("day", "Day School"),
        ("boarding", "Boarding School"),
        ("both", "Day & Boarding"),
    ]

    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=80, blank=True)
    motto = models.CharField(max_length=255, blank=True)
    registration_number = models.CharField(max_length=100, blank=True)

    school_type = models.CharField(
        max_length=20,
        choices=SCHOOL_TYPE_CHOICES,
        default="both"
    )
    school_mode = models.CharField(
        max_length=20,
        choices=SCHOOL_MODE_CHOICES,
        default="day"
    )

    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    address = models.TextField(blank=True)

    logo = models.ImageField(upload_to="schools/logos/", blank=True, null=True)

    currency = models.CharField(max_length=10, default="TZS")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "School Profile"
        verbose_name_plural = "School Profile"

    def __str__(self):
        return self.name


class SchoolBranch(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    manager_name = models.CharField(max_length=120, blank=True)
    is_main_branch = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class SystemSetting(models.Model):
    ATTENDANCE_MODE_CHOICES = [
        ("manual", "Manual Attendance"),
        ("biometric", "Biometric Attendance"),
        ("both", "Manual & Biometric"),
    ]

    default_currency = models.CharField(max_length=10, default="TZS")
    academic_year_auto_create = models.BooleanField(default=False)
    enable_sms_notifications = models.BooleanField(default=False)
    enable_email_notifications = models.BooleanField(default=False)
    enable_parent_portal = models.BooleanField(default=False)
    enable_student_portal = models.BooleanField(default=False)

    attendance_mode = models.CharField(
        max_length=20,
        choices=ATTENDANCE_MODE_CHOICES,
        default="manual"
    )

    receipt_prefix = models.CharField(max_length=30, default="RCPT")
    invoice_prefix = models.CharField(max_length=30, default="INV")
    admission_prefix = models.CharField(max_length=30, default="SLA")

    low_stock_alert_level = models.PositiveIntegerField(default=5)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"

    def __str__(self):
        return "System Settings"