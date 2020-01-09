import googleapiclient.discovery
import os
import slack

from django.conf import settings
from google.oauth2 import service_account


class GoogleApiClient:
    '''
    This is a wrapper class around the Google API client.

    This is a singleton class.
    '''
    __instance = None

    @staticmethod
    def getInstance():
        ''' Static access method. '''
        if GoogleApiClient.__instance == None:
            GoogleApiClient()
        return GoogleApiClient.__instance

    def __init__(self):
        ''' Private constructor. '''
        if GoogleApiClient.__instance != None:
            raise Exception("GoogleApiClient is a singleton and should not be "
                            "constructed multiple times. Use "
                            "GoogleApiClient.getInstance() to access it.")

        if not settings.GOOGLE_API_AUTHN_INFO:
            return None

        credentials = service_account.Credentials.from_service_account_info(
            settings.GOOGLE_API_AUTHN_INFO,
            scopes=settings.GOOGLE_DRIVE_PERMISSIONS_SCOPES
        )

        self._drive_service = googleapiclient.discovery.build('drive', 'v3', credentials=credentials)
        self._sheets_service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)

        GoogleApiClient.__instance = self

    @staticmethod
    def __extract_id_from_sheets_url(url):
        '''
        Assumes `url` is of the form
        https://docs.google.com/spreadsheets/d/<ID>/edit...
        and returns the <ID> portion
        '''
        start = url.find('/d/') + 3
        end = url.find('/edit')
        return url[start:end]

    def create_google_sheets(self, name):
        req_body = {
            'name': name
        }
        response = self._drive_service.files().copy(
            fileId=settings.GOOGLE_SHEETS_TEMPLATE_FILE_ID,
            body=req_body,
            fields='webViewLink',
        ).execute()

        link = response['webViewLink']
        return link

    def add_puzzle_and_slack_links_to_sheet(self, puzzle_url, slack_channel_id,
                                            sheet_url):
        req_body = {
            'values': [
                ['Puzzle link', puzzle_url],
                ['Slack channel', '%s/app_redirect?channel=%s'
                                  % (settings.SLACK_BASE_URL, slack_channel_id)]
            ]
        }
        self._sheets_service.spreadsheets().values().update(
            spreadsheetId=self.__extract_id_from_sheets_url(sheet_url),
            range='A1:B2',
            valueInputOption='RAW',
            body=req_body
        ).execute()

    def get_file_user_emails(self, file_id):
        response = self._drive_service.files().get(
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
