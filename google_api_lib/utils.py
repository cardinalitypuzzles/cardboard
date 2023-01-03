import logging

import googleapiclient
import googleapiclient.discovery
import googleapiclient.errors
from celery import Task
from django.conf import settings
from google.oauth2 import service_account

logger = logging.getLogger(__name__)


def enabled():
    return settings.GOOGLE_API_AUTHN_INFO is not None


class GoogleApiClientTask(Task):
    autoretry_for = (googleapiclient.errors.Error,)
    retry_kwargs = {"max_retries": 5}
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True

    def __init__(self):
        if not enabled():
            return

        self._credentials = service_account.Credentials.from_service_account_info(
            settings.GOOGLE_API_AUTHN_INFO,
            scopes=settings.GOOGLE_DRIVE_PERMISSIONS_SCOPES,
        )

    def drive_service(self):
        return googleapiclient.discovery.build(
            "drive", "v3", credentials=self._credentials, cache_discovery=False
        )

    def drive_activity_service(self):
        return googleapiclient.discovery.build(
            "driveactivity", "v2", credentials=self._credentials, cache_discovery=False
        )

    def sheets_service(self):
        return googleapiclient.discovery.build(
            "sheets", "v4", credentials=self._credentials, cache_discovery=False
        )

    def sheets_owner(self, file_id):
        """Returns the owner of the provided Sheet."""
        file = (
            self.drive_service().files().get(fileId=file_id, fields="owners").execute()
        )
        return file["owners"][0]["emailAddress"]
