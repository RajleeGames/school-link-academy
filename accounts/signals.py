from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        role = "admin" if instance.is_superuser else "support_staff"

        UserProfile.objects.create(
            user=instance,
            role=role,
            is_active_profile=True
        )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, "account_profile"):
        instance.account_profile.save()