# accounts/permissions.py

ROLE_LABELS = {
    "admin": "Administrator",
    "head_teacher": "Head Teacher",
    "academic_master": "Academic Master",
    "secretary": "Secretary / Receptionist",
    "cashier": "Cashier",
    "accountant": "Accountant / Bursar",
    "teacher": "Teacher",
    "librarian": "Librarian",
    "hostel_manager": "Hostel Manager",
    "transport_manager": "Transport Manager",
    "stock_keeper": "Stock Keeper",
    "parent": "Parent / Guardian",
    "support_staff": "Support Staff",
}


ALL_PERMISSIONS = {
    # Dashboard
    "dashboard.view": "View Admin Dashboard",

    # School setup
    "school.profile.view": "View School Profile",
    "school.profile.edit": "Edit School Profile",
    "school.branches.view": "View School Branches",
    "school.branches.manage": "Manage School Branches",
    "school.settings.view": "View System Settings",
    "school.settings.manage": "Manage System Settings",
    "users.roles.view": "View User Roles",
    "users.roles.manage": "Manage User Roles",

    # Students / parents / staff
    "students.view": "View Students",
    "students.manage": "Manage Students",
    "parents.view": "View Parents",
    "parents.manage": "Manage Parents",
    "parents.login.manage": "Create Parent Login",
    "staff.view": "View Staff",
    "staff.manage": "Manage Staff",
    "admissions.view": "View Admissions",
    "admissions.manage": "Manage Admissions",

    # Academics
    "academics.view": "View Academic Setup",
    "academics.manage": "Manage Academic Setup",
    "subjects.view": "View Subjects",
    "subjects.manage": "Manage Subjects",

    # Attendance
    "attendance.view": "View Attendance",
    "attendance.manage_students": "Manage Student Attendance",
    "attendance.manage_staff": "Manage Staff Attendance",
    "attendance.reports": "View Attendance Reports",

    # Exams
    "exams.view": "View Exams",
    "exams.manage": "Manage Exams",
    "results.view": "View Results",
    "results.manage": "Manage Results",
    "results.reports": "View Result Reports",

    # Finance
    "fees.view": "View Fees",
    "fees.setup": "Manage Fee Setup",
    "invoices.view": "View Invoices",
    "invoices.manage": "Manage Invoices",
    "payments.view": "View Payments",
    "payments.manage": "Record Payments",
    "debtors.view": "View Debtors",
    "fees.reports": "View Fee Reports",

    # Expenses
    "expenses.view": "View Expenses",
    "expenses.manage": "Manage Expenses",
    "expenses.reports": "View Expense Reports",

    # Operations
    "timetable.view": "View Timetable",
    "timetable.manage": "Manage Timetable",
    "homework.view": "View Homework",
    "homework.manage": "Manage Homework",
    "discipline.view": "View Discipline",
    "discipline.manage": "Manage Discipline",
    "library.view": "View Library",
    "library.manage": "Manage Library",
    "hostel.view": "View Hostel",
    "hostel.manage": "Manage Hostel",
    "transport.view": "View Transport",
    "transport.manage": "Manage Transport",
    "inventory.view": "View Inventory",
    "inventory.manage": "Manage Inventory",
    "payroll.view": "View Payroll",
    "payroll.manage": "Manage Payroll",

    # Reports
    "reports.view": "View Reports",
    "reports.students": "View Student Reports",
    "reports.finance": "View Finance Reports",
    "reports.exams": "View Exam Reports",

    # Parent portal
    "parent.portal.view": "View Parent Portal",
    "parent.invoices.view": "View Child Invoices",
    "parent.payments.view": "View Child Payments",
    "parent.results.view": "View Child Results",
    "parent.attendance.view": "View Child Attendance",
}


ROLE_PERMISSIONS = {
    "admin": list(ALL_PERMISSIONS.keys()),

    "head_teacher": [
        "dashboard.view",
        "school.profile.view",
        "school.branches.view",

        "students.view",
        "parents.view",
        "staff.view",
        "admissions.view",

        "academics.view",
        "academics.manage",
        "subjects.view",
        "subjects.manage",

        "attendance.view",
        "attendance.manage_students",
        "attendance.manage_staff",
        "attendance.reports",

        "exams.view",
        "exams.manage",
        "results.view",
        "results.manage",
        "results.reports",

        "timetable.view",
        "timetable.manage",
        "homework.view",
        "discipline.view",

        "reports.view",
        "reports.students",
        "reports.exams",
    ],

    "academic_master": [
        "dashboard.view",

        "students.view",
        "parents.view",

        "academics.view",
        "academics.manage",
        "subjects.view",
        "subjects.manage",

        "attendance.view",
        "attendance.manage_students",
        "attendance.reports",

        "exams.view",
        "exams.manage",
        "results.view",
        "results.manage",
        "results.reports",

        "timetable.view",
        "timetable.manage",
        "homework.view",
        "homework.manage",
        "discipline.view",

        "reports.view",
        "reports.students",
        "reports.exams",
    ],

    "secretary": [
        "dashboard.view",

        "students.view",
        "students.manage",
        "parents.view",
        "parents.manage",
        "parents.login.manage",
        "admissions.view",
        "admissions.manage",

        "attendance.view",
        "attendance.manage_students",
        "attendance.reports",

        "reports.view",
        "reports.students",
    ],

    "cashier": [
        "dashboard.view",

        "students.view",
        "parents.view",

        "fees.view",
        "invoices.view",
        "payments.view",
        "payments.manage",
        "debtors.view",
        "fees.reports",

        "reports.view",
        "reports.finance",
    ],

    "accountant": [
        "dashboard.view",

        "students.view",
        "parents.view",

        "fees.view",
        "fees.setup",
        "invoices.view",
        "invoices.manage",
        "payments.view",
        "payments.manage",
        "debtors.view",
        "fees.reports",

        "expenses.view",
        "expenses.manage",
        "expenses.reports",

        "payroll.view",
        "payroll.manage",

        "reports.view",
        "reports.finance",
    ],

    "teacher": [
        # Teacher should NOT see full admin setup.
        # Teacher can see teaching-related pages only.
        "dashboard.view",

        "students.view",

        "academics.view",
        "subjects.view",

        "attendance.view",
        "attendance.manage_students",
        "attendance.reports",

        "exams.view",
        "results.view",
        "results.manage",

        "timetable.view",
        "homework.view",
        "homework.manage",
        "discipline.view",

        
        "reports.exams",
    ],

    "librarian": [
        "dashboard.view",
        "students.view",
        "library.view",
        "library.manage",
        
    ],

    "hostel_manager": [
        "dashboard.view",
        "students.view",
        "hostel.view",
        "hostel.manage",
        "reports.view",
    ],

    "transport_manager": [
        "dashboard.view",
        "students.view",
        "transport.view",
        "transport.manage",
        "reports.view",
    ],

    "stock_keeper": [
        "dashboard.view",
        "inventory.view",
        "inventory.manage",
        "reports.view",
    ],

    "parent": [
        "parent.portal.view",
        "parent.invoices.view",
        "parent.payments.view",
        "parent.results.view",
        "parent.attendance.view",
    ],

    "support_staff": [
        "dashboard.view",
    ],
}


def get_user_role(user):
    if not user or not user.is_authenticated:
        return None

    if user.is_superuser:
        return "admin"

    profile = getattr(user, "account_profile", None)

    if not profile:
        return None

    if not profile.is_active_profile:
        return None

    return profile.role


def get_role_permissions(role):
    if not role:
        return []

    return ROLE_PERMISSIONS.get(role, [])


def user_has_permission(user, permission_code):
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    role = get_user_role(user)

    if not role:
        return False

    return permission_code in get_role_permissions(role)


def user_has_any_permission(user, permission_codes):
    return any(user_has_permission(user, code) for code in permission_codes)


def user_has_all_permissions(user, permission_codes):
    return all(user_has_permission(user, code) for code in permission_codes)