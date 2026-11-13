import logging
import re
from urllib.parse import parse_qs, urlparse

import googleapiclient
import googleapiclient.discovery
import googleapiclient.errors
from celery import Task
from django.conf import settings
from google.oauth2 import service_account

logger = logging.getLogger(__name__)


def extract_google_id(value: str) -> str:
    """Extracts a Google Drive/Sheets ID from either a raw ID or a Drive/Docs URL."""
    value = value.strip()
    if not value:
        return ""

    if "/" not in value and "?" not in value:
        return value

    parsed = urlparse(value if "://" in value else f"https://{value}")
    query_params = parse_qs(parsed.query)
    if "id" in query_params and query_params["id"]:
        return query_params["id"][0]

    match = re.search(r"/(?:folders|d)/([A-Za-z0-9_-]+)", parsed.path)
    if match:
        return match.group(1)

    raise ValueError("Could not extract a valid Google Drive or Sheets ID.")


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

    def people_service(self):
        return googleapiclient.discovery.build(
            "people", "v1", credentials=self._credentials, cache_discovery=False
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
