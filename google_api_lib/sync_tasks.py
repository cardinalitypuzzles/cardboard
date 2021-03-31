from .utils import GoogleApiClientTask
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

HUMAN_DRIVE_FOLDER_NAME = "FOLDER FOR HUMANS"


@shared_task(base=GoogleApiClientTask, bind=True)
def get_file_user_emails(self, file_id) -> List[str]:
    response = (
        self.drive_service().files().get(fileId=file_id, fields="permissions").execute()
    )

    permissions = response["permissions"]

    emails = set()
    for perm in permissions:
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
