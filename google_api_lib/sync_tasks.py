from .utils import GoogleApiClientTask
from celery import shared_task


@shared_task(base=GoogleApiClientTask, bind=True)
def get_file_user_emails(self, file_id):
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
