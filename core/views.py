from django.conf import settings
from django.shortcuts import redirect
from django.utils import translation


def switch_language(request):
    language = request.POST.get("language", "en")
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"

    allowed_languages = [code for code, name in settings.LANGUAGES]

    if language not in allowed_languages:
        language = settings.LANGUAGE_CODE

    translation.activate(language)

    request.session["django_language"] = language
    request.session[settings.LANGUAGE_COOKIE_NAME] = language

    response = redirect(next_url)
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        language,
        max_age=60 * 60 * 24 * 365,
        path="/",
        samesite="Lax",
    )

    return response