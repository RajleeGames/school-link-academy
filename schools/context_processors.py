from .models import SchoolProfile


def school_profile_context(request):
    profile = SchoolProfile.objects.filter(is_active=True).first()

    if not profile:
        profile = SchoolProfile.objects.first()

    return {
        "school_profile_global": profile
    }