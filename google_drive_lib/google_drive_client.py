import googleapiclient.discovery
import os
import slack

from django.conf import settings
from google.oauth2 import service_account


class GoogleDriveClient:
    '''
    This is a wrapper class around the Google Drive API client.

    This is a singleton class.
    '''
    __instance = None

    @staticmethod
    def getInstance():
        ''' Static access method. '''
        if GoogleDriveClient.__instance == None:
            GoogleDriveClient()
        return GoogleDriveClient.__instance

    def __init__(self):
        ''' Private constructor. '''
        if GoogleDriveClient.__instance != None:
            raise Exception("GoogleDriveClient is a singleton and should not be "
                            "constructed multiple times. Use "
                            "GoogleDriveClient.getInstance() to access it.")

        if not settings.GOOGLE_DRIVE_API_AUTHN_INFO:
            return None

        credentials = service_account.Credentials.from_service_account_info(
            settings.GOOGLE_DRIVE_API_AUTHN_INFO,
            scopes=settings.GOOGLE_DRIVE_PERMISSIONS_SCOPES
        )

        self._service = googleapiclient.discovery.build('drive', 'v3', credentials=credentials)

        GoogleDriveClient.__instance = self

    def create_google_sheets(self, name):
        req_body = {
            'name': name
        }
        response = self._service.files().copy(
            fileId=settings.GOOGLE_SHEETS_TEMPLATE_FILE_ID,
            body=req_body,
            fields='webViewLink',
        ).execute()

        link = response['webViewLink']
        return link

    def get_file_user_emails(self, file_id):
        response = self._service.files().get(
            fileId=file_id,
            fields='permissions'
        ).execute()

        permissions = response['permissions']

        emails = set()
        for perm in permissions:
            email = perm['emailAddress']
            emails.add(email)
            emails.add(email.lower())

        return sorted(list(emails))
