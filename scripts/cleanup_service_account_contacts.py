import datetime

import googleapiclient
from django.conf import settings
from google.oauth2 import service_account

from accounts.models import Puzzler

# Clear service account contact list

credentials = service_account.Credentials.from_service_account_info(
    settings.GOOGLE_API_AUTHN_INFO,
    scopes=settings.GOOGLE_DRIVE_PERMISSIONS_SCOPES,
)

people_service = googleapiclient.discovery.build(
    "people", "v1", credentials=credentials, cache_discovery=False
)

response = (
    people_service.people()
    .connections()
    .list(resourceName="people/me", personFields="emailAddresses")
    .execute()
)

for connection in response["connections"]:
    people_service.people().deleteContact(
        resourceName=connection["resourceName"]
    ).execute()
