from django.conf import settings


def google_auth(request):
    return {
        "is_google_auth_enabled": True
        if settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
        else False
    }


def app_info(request):
    return {
        "APP_SHORT_TITLE": settings.APP_SHORT_TITLE,
        "APP_TITLE": settings.APP_TITLE,
        "CONTACT_AUTHOR_NAME": settings.CONTACT_AUTHOR_NAME,
        "CONTACT_EMAIL": settings.CONTACT_EMAIL,
    }
