# accounts/management/commands/seed_role_permissions.py

from django.core.management.base import BaseCommand

from accounts.permissions import ALL_PERMISSIONS, ROLE_LABELS, ROLE_PERMISSIONS


class Command(BaseCommand):
    help = "Show and validate School Link roles and permissions"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("School Link Role Permissions"))
        self.stdout.write("=" * 60)

        for role, label in ROLE_LABELS.items():
            permissions = ROLE_PERMISSIONS.get(role, [])

            self.stdout.write("")
            self.stdout.write(self.style.WARNING(f"{label} ({role})"))
            self.stdout.write("-" * 60)

            if not permissions:
                self.stdout.write("No permissions assigned.")
                continue

            for permission_code in permissions:
                permission_name = ALL_PERMISSIONS.get(permission_code)

                if permission_name:
                    self.stdout.write(f"  ✅ {permission_code} - {permission_name}")
                else:
                    self.stdout.write(
                        self.style.ERROR(f"  ❌ {permission_code} - NOT FOUND IN ALL_PERMISSIONS")
                    )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Done."))