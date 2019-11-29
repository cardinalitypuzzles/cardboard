from django.conf import settings


def google_auth(request):
    return {'is_google_auth_enabled': True if settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET else False}
