from .utils import GoogleApiClientTask
from celery import shared_task
from django.conf import settings
from googleapiclient.errors import Error
from social_core.exceptions import AuthForbidden
from typing import List

import logging

logger = logging.getLogger(__name__)

HUMAN_DRIVE_FOLDER_NAME = "FOLDER FOR HUMANS"


def auth_allowed(backend, details, response, *args, **kwargs):
    """
    Checks if a user is allowed by checking if the user's email
    is in the list of emails added to the Google Drive folder.
    Part of the SOCIAL_AUTH_PIPELINE (see settings.py).
    """
    email = details.get("email").lower()
    # Allow all emails if Google Drive integration is not set up
    # or folder is world readable. Otherwise, only allow emails
    # added to the Google Drive folder.
    if settings.GOOGLE_API_AUTHN_INFO:
        user_emails = get_file_user_emails(settings.GOOGLE_DRIVE_HUNT_FOLDER_ID)
        if user_emails and email not in user_emails:
            raise AuthForbidden(backend)


@shared_task(base=GoogleApiClientTask, bind=True)
def get_file_user_emails(self, file_id) -> List[str]:
    response = (
        self.drive_service().files().get(fileId=file_id, fields="permissions").execute()
    )

    permissions = response["permissions"]

    emails = set()
    for perm in permissions:
        if perm["id"] == "anyoneWithLink":
            return None
        email = perm["emailAddress"]
        emails.add(email)
        emails.add(email.lower())

    return sorted(list(emails))


@shared_task(base=GoogleApiClientTask, bind=True)
def get_human_drive_folder(self, file_id) -> str:
    drive_service = self.drive_service()

    q = (
        f"'{file_id}' in parents and "
        + f"name='{HUMAN_DRIVE_FOLDER_NAME}' and "
        + "mimeType = 'application/vnd.google-apps.folder'"
    )
    response = (
        drive_service.files()
        .list(q=q, spaces="drive", fields="files(webViewLink)")
        .execute()
    )

    human_folders = response.get("files", [])
    if len(human_folders) > 0:
        if len(human_folders) > 1:
            logger.warn(
                f"Multiple folders for humans: "
                + ", ".join([f["webViewLink"] for f in human_folders])
            )

        return human_folders[0]["webViewLink"]

    file_metadata = {
        "name": HUMAN_DRIVE_FOLDER_NAME,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [file_id],
    }

    human_folder = (
        drive_service.files().create(body=file_metadata, fields="webViewLink").execute()
    )
    return human_folder["webViewLink"]
