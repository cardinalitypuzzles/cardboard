from django.conf import settings
import googleapiclient
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2 import service_account

from celery import Task
import re
import logging

logger = logging.getLogger(__name__)


def enabled():
    return settings.GOOGLE_API_AUTHN_INFO is not None


def extract_id_from_sheets_url(url):
    """
    Assumes `url` is of the form
    https://docs.google.com/spreadsheets/d/<ID>/...
    and returns the <ID> portion
    """
    pattern = ".*docs\.google\.com\/spreadsheets\/d\/([-\w]+).*"
    m = re.search(pattern, url)
    if m is None:
        logger.error(f"Invalid url: {url}")
        return ""
    return m.group(1)


def extract_id_from_drive_folder_url(url):
    """
    Assumes `url` is of the form
    https://drive.google.com/drive/u/2/folders/<ID>/..
    and returns the <ID> portion
    """
    pattern = ".*drive\.google\.com\/drive\/u\/2\/folders\/([-\w]+).*"
    m = re.search(pattern, url)
    if m is None:
        logger.error(f"Invalid url: {url}")
        return ""
    return m.group(1)


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

        template = (
            self.drive_service()
            .files()
            .get(fileId=settings.GOOGLE_SHEETS_TEMPLATE_FILE_ID, fields="owners")
            .execute()
        )
        self._sheets_owner = template["owners"][0]["emailAddress"]

    def drive_service(self):
        return googleapiclient.discovery.build(
            "drive", "v3", credentials=self._credentials, cache_discovery=False
        )

    def sheets_service(self):
        return googleapiclient.discovery.build(
            "sheets", "v4", credentials=self._credentials, cache_discovery=False
        )
