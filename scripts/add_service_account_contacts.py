import datetime

import googleapiclient
from django.conf import settings
from google.oauth2 import service_account

from accounts.models import Puzzler

# For adding all registered user into service account's contact list
# Needed on a one-off basis for people API to work to populate UIDs
# of users that were created before we started storing that data

credentials = service_account.Credentials.from_service_account_info(
    settings.GOOGLE_API_AUTHN_INFO,
    scopes=settings.GOOGLE_DRIVE_PERMISSIONS_SCOPES,
)

people_service = googleapiclient.discovery.build(
    "people", "v1", credentials=credentials, cache_discovery=False
)

for p in Puzzler.objects.all():
    if not p.social_auth.exists():
        continue
    print(str(p))
    response = (
        people_service.people()
        .createContact(
            body={
                "names": [{"givenName": str(p)}],
                "emailAddresses": [{"value": p.email}],
            }
        )
        .execute()
    )
