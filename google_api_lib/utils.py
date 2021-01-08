import googleapiclient
import googleapiclient.discovery
from django.conf import settings
from google.oauth2 import service_account


from celery import Task


def enabled():
    return settings.GOOGLE_API_AUTHN_INFO is not None


class GoogleApiClientTask(Task):
    def __init__(self):
        if not enabled():
            return

        self._credentials = service_account.Credentials.from_service_account_info(
            settings.GOOGLE_API_AUTHN_INFO,
            scopes=settings.GOOGLE_DRIVE_PERMISSIONS_SCOPES,
        )
        self._drive_service = googleapiclient.discovery.build(
            "drive", "v3", credentials=self._credentials
        )
        self._sheets_service = googleapiclient.discovery.build(
            "sheets", "v4", credentials=self._credentials
        )
