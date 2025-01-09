import datetime
import itertools
import logging
import random
import re
import time
from typing import List, Optional

import dateutil.parser
from celery import shared_task
from dateutil import tz
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from django.db.models import CharField, F, Value
from django.db.models.functions import Concat
from googleapiclient import _auth
from guardian.shortcuts import assign_perm

from cardboard.settings import TaskPriority
from chat.tasks import handle_sheet_created
from hunts.models import Hunt
from puzzles.models import Puzzle, PuzzleActivity

from .utils import GoogleApiClientTask, enabled

logger = logging.getLogger(__name__)


# helper function that can be mocked for testing
def create_google_sheets_helper(self, name, template_file_id) -> dict:
    req_body = {"name": name}
    # copy template sheet
    file = (
        self.drive_service()
        .files()
        .copy(
            fileId=template_file_id,
            body=req_body,
            fields="id,webViewLink,permissions",
        )
        .execute()
    )
    return file


def maybe_get_renamable_sheet_for_puzzle(self, puzzle):
    """Returns a sheet ID for a spare template file that can be assigned to this puzzle (without making a copy)."""

    template_folder_id = puzzle.hunt.settings.google_sheets_template_folder_id
    if not template_folder_id:
        return None

    response = (
        self.drive_service()
        .files()
        .list(
            corpora="user",
            q=f"'{template_folder_id}' in parents",
            fields="files(id,webViewLink,permissions)",
        )
        .execute()
    )
    files = response.get("files", [])
    if len(files) == 0:
        logger.warn(
            f"The Drive template folder {template_folder_id} for hunt {puzzle.hunt.name} is empty"
        )
        return None

    # Return a random file to reduce race conditions or problems with a specific file
    return random.choice(files)


@shared_task(base=GoogleApiClientTask, bind=True)
def move_drive_file(self, file_id, destination_folder_id) -> None:
    file = self.drive_service().files().get(fileId=file_id, fields="parents").execute()

    self.drive_service().files().update(
        fileId=file_id,
        addParents=destination_folder_id,
        removeParents=",".join(file["parents"]),
    ).execute()


# transfer new sheet ownership back to OG owner, so that scripts can run
@shared_task(base=GoogleApiClientTask, bind=True)
def transfer_ownership(self, file, template_file_id) -> None:
    new_owner = self.sheets_owner(template_file_id)
    permission = next(p for p in file["permissions"] if p["emailAddress"] == new_owner)
    self.drive_service().permissions().update(
        fileId=file["id"],
        permissionId=permission["id"],
        body={"role": "writer", "pendingOwner": "true"},
    ).execute()


@shared_task(
    base=GoogleApiClientTask,
    bind=True,
    priority=TaskPriority.HIGH.value,
    time_limit=150,
    soft_time_limit=120,
    retry_backoff=True,
    default_retry_delay=30,
)
def create_google_sheets(self, puzzle_id) -> None:
    with transaction.atomic():
        puzzle = Puzzle.objects.select_related("hunt__settings").get(pk=puzzle_id)
        template_file_id = (
            puzzle.hunt.settings.google_sheets_template_file_id
            or settings.GOOGLE_SHEETS_TEMPLATE_FILE_ID
        )
        destination_folder_id = (
            puzzle.hunt.settings.google_drive_folder_id
            or settings.GOOGLE_DRIVE_HUNT_FOLDER_ID
        )

        new_file = None

        existing_file = maybe_get_renamable_sheet_for_puzzle(self, puzzle)
        if existing_file:
            new_file = existing_file
        else:
            if not template_file_id:
                logging.warn(
                    f"Cannot create a sheet for {puzzle.name} as we can't find a sheets template"
                )
                return
            new_file = create_google_sheets_helper(self, puzzle.name, template_file_id)

        sheet_url = new_file["webViewLink"]
        puzzle.sheet = sheet_url
        puzzle.save()

        def post_create_tasks():
            if existing_file:
                # We copied over an existing file, but we haven't renamed it yet
                rename_sheet.delay(sheet_url, puzzle.name)

            transfer_ownership.delay(new_file, template_file_id)
            add_puzzle_link_to_sheet.delay(puzzle.url, sheet_url)

            if destination_folder_id:
                move_drive_file.delay(
                    file_id=new_file["id"], destination_folder_id=destination_folder_id
                )
            else:
                logging.warn(
                    f"Cannot move the new puzzle for {puzzle.name} as we can't find a drive folder"
                )

            if puzzle.chat_room:
                handle_sheet_created.delay(puzzle_id)

        # Only run these other tasks if we successfully commit this particular sheet ID
        # We might not be able to if there's some race condition
        # (for example, two puzzles claiming the same sheet at the same time)
        transaction.on_commit(post_create_tasks)


def extract_id_from_sheets_url(url) -> str:
    """
    Assumes `url` is of the form
    https://docs.google.com/spreadsheets/d/<ID>/edit...
    and returns the <ID> portion
    """
    start = url.find("/d/") + 3
    end = url.find("/edit")
    return url[start:end]


@shared_task(base=GoogleApiClientTask, bind=True)
def add_puzzle_link_to_sheet(self, puzzle_url, sheet_url) -> None:
    req_body = {
        "values": [
            [f'=HYPERLINK("{puzzle_url}", "Puzzle Link")'],
        ]
    }
    self.sheets_service().spreadsheets().values().update(
        spreadsheetId=extract_id_from_sheets_url(sheet_url),
        range="A1:B2",
        valueInputOption="USER_ENTERED",
        body=req_body,
    ).execute()


@shared_task(base=GoogleApiClientTask, bind=True)
def rename_sheet(self, sheet_url, name) -> None:
    requests = [
        {
            "updateSpreadsheetProperties": {
                "properties": {
                    "title": name,
                },
                "fields": "title",
            }
        }
    ]
    body = {"requests": requests}
    self.sheets_service().spreadsheets().batchUpdate(
        spreadsheetId=extract_id_from_sheets_url(sheet_url), body=body
    ).execute()


# create new tab in spreadsheet_id with given title
def _add_sheet(sheets_service, http, spreadsheet_id, title) -> str:
    requests = [
        {
            "addSheet": {
                "properties": {
                    "title": title,
                },
            },
        }
    ]
    response = (
        sheets_service.spreadsheets()
        .batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests},
            fields="replies.addSheet.properties.sheetId",
        )
        .execute(http=http)
    )
    return response["replies"][-1]["addSheet"]["properties"]["sheetId"]


def _clear_sheet(sheets_service, http, spreadsheet_id, sheet_id) -> None:
    requests = [
        {
            "updateCells": {
                "range": {"sheetId": sheet_id},
                "fields": "userEnteredValue,userEnteredFormat",
            }
        }
    ]

    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": requests},
    ).execute(http=http)


def _build_feeder_table(feeders) -> int:
    feeders_to_answers = {f: f.correct_answers() for f in feeders}

    if len(feeders_to_answers) > 0:
        max_num_answers = max(1, max((len(v) for v in feeders_to_answers.values())))
    else:
        max_num_answers = 1

    def _get_answer_or_blank(puzzle, i):
        if i < len(feeders_to_answers[puzzle]):
            return feeders_to_answers[puzzle][i]
        return ""

    header = [
        {
            "userEnteredValue": {"stringValue": h},
            "userEnteredFormat": {"textFormat": {"bold": True}},
        }
        for h in (
            ["Puzzle Link", "Sheet", "Puzzle Name"] + ["Answer"] * max_num_answers
        )
    ]

    table = [
        {
            "values": header,
        }
    ]
    for puzzle in feeders:
        row = [
            {
                "userEnteredValue": {
                    "formulaValue": '=HYPERLINK("%s", "puzzle")' % puzzle.url
                }
            },
            {
                "userEnteredValue": {
                    "formulaValue": '=HYPERLINK("%s", "sheet")' % puzzle.sheet
                }
            },
            {"userEnteredValue": {"stringValue": puzzle.name}},
        ] + [
            {
                "userEnteredValue": {"stringValue": _get_answer_or_blank(puzzle, i)},
                "userEnteredFormat": {"textFormat": {"fontFamily": "Roboto Mono"}},
            }
            for i in range(max_num_answers)
        ]

        table.append({"values": row})

    return table


@shared_task(base=GoogleApiClientTask, bind=True, priority=TaskPriority.LOW.value)
def _update_meta_sheet_feeders(self, puzzle_id) -> None:
    """
    Updates the input meta puzzle's spreadsheet with the
    latest feeder puzzle info
    """
    meta_puzzle = Puzzle.objects.get(pk=puzzle_id)
    if not meta_puzzle.is_meta or not meta_puzzle.sheet:
        return

    logger.info(
        "Starting updating the meta sheet for '%s' " "with feeder puzzles" % meta_puzzle
    )
    spreadsheet_id = extract_id_from_sheets_url(meta_puzzle.sheet)
    feeders = meta_puzzle.feeders.all()
    feeders = sorted(feeders, key=lambda p: p.name)
    feeder_table = _build_feeder_table(feeders)
    width = len(feeder_table[0]["values"])

    grandfeeder_tables = {}
    for feeder in feeders:
        if feeder.is_meta:
            feeders_of_feeders = sorted(feeder.feeders.all(), key=lambda p: p.name)
            grandfeeder_table = _build_feeder_table(feeders_of_feeders)
            grandfeeder_tables[feeder.name] = grandfeeder_table
            width = max(width, len(grandfeeder_table[0]["values"]))

    rows = [
        {
            "values": [
                {
                    "userEnteredValue": {
                        "stringValue": "THIS PAGE IS AUTOGENERATED AND WILL BE OVERWRITTEN WHEN THERE ARE PUZZLE UPDATES."
                    }
                }
            ]
        },
        {
            "values": [
                {"userEnteredValue": {"stringValue": "COPY INFO TO ANOTHER SHEET."}}
            ]
        },
        {},
    ] + feeder_table

    for feeder_name, grandfeeder_table in grandfeeder_tables.items():
        rows.append({})
        rows.append(
            {
                "values": [
                    {
                        "userEnteredValue": {
                            "stringValue": "Feeders of %s" % feeder_name
                        },
                        "userEnteredFormat": {"textFormat": {"bold": True}},
                    }
                ]
            }
        )
        # ignore headers
        rows += grandfeeder_table[1:]

    # Each thread needs its own http object because httplib2.Http()
    # is used under the hood and that is not thread safe.
    # Ref: https://github.com/googleapis/google-api-python-client/blob/master/docs/thread_safety.md
    http = _auth.authorized_http(self._credentials)
    sheets_service = self.sheets_service()
    response = (
        sheets_service.spreadsheets()
        .get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties.title,sheets.properties.sheetId,sheets.protectedRanges",
        )
        .execute(http=http)
    )

    sheet_id = None
    protected_range_id = None
    for sheet in response["sheets"]:
        if sheet["properties"]["title"] == "Feeders":
            sheet_id = sheet["properties"]["sheetId"]
            if "protectedRanges" in sheet and len(sheet["protectedRanges"]) > 0:
                protected_range_id = sheet["protectedRanges"][0]["protectedRangeId"]
            break

    if sheet_id is None:
        # create Feeders tab if it does not exist
        sheet_id = _add_sheet(sheets_service, http, spreadsheet_id, "Feeders")
    else:
        # otherwise, clear the sheet
        _clear_sheet(sheets_service, http, spreadsheet_id, sheet_id)

    requests = [
        {
            "updateCells": {
                "fields": "userEnteredFormat.textFormat.fontFamily,"
                "userEnteredValue.stringValue,"
                "userEnteredValue.formulaValue,"
                "userEnteredFormat.textFormat.bold",
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": len(rows),
                    "startColumnIndex": 0,
                    "endColumnIndex": width,
                },
                "rows": rows,
            },
        },
        {
            "autoResizeDimensions": {
                "dimensions": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 1,
                    "endIndex": width,
                },
            },
        },
    ]
    if protected_range_id is None:
        requests.append(
            {
                "addProtectedRange": {
                    "protectedRange": {
                        "range": {
                            "sheetId": sheet_id,
                        },
                        "description": "Autogenerated page",
                        "warningOnly": False,
                        "editors": {
                            "users": settings.GOOGLE_API_AUTHN_INFO["client_email"]
                        },
                    }
                }
            }
        )

    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body={"requests": requests}
    ).execute(http=http)
    logger.info(
        "Done updating the meta sheet for '%s' " "with feeder puzzles" % meta_puzzle
    )


def update_meta_and_metameta_sheets_delayed(meta):
    _update_meta_sheet_feeders.delay(meta.id)

    for metameta in meta.metas.all():
        _update_meta_sheet_feeders.delay(metameta.id)


def extract_id_from_person_name(person_name) -> Optional[str]:
    """
    Person name is identifier for Google People API and is of the format `people/ACCOUNT_ID`
    See https://developers.google.com/drive/activity/v2/reference/rest/v2/activity/user
    and https://developers.google.com/people/ for more.
    Returns the <ACCOUNT_ID> portion
    """
    result = re.search("people/([0-9]+)", person_name)
    return result.group(1) if result else None


def extract_id_from_drive_item_name(drive_item_name) -> Optional[str]:
    """
    Drive item identifiers are of the format `items/ITEM_ID`
    See https://developers.google.com/drive/activity/v2/reference/rest/v2/activity/driveitem#DriveItem
    for more.
    Returns the <ITEM_ID> portion
    """
    result = re.search("items/(.+)", drive_item_name)
    return result.group(1) if result else None


def get_puzzler_from_uid(google_api_client, uid) -> Optional[str]:
    UserModel = get_user_model()
    try:
        return UserModel.objects.get(social_auth__uid=uid)
    except UserModel.DoesNotExist:
        pass

    # Fall back to People API
    # Note that this API depends on the email being added as service account's contact list
    # It also has a tight request limit
    time.sleep(1)

    response = (
        google_api_client.people_service()
        .people()
        .get(resourceName=f"people/{uid}", personFields="emailAddresses")
        .execute()
    )

    emails = response.get("emailAddresses", [])
    emails = [email.get("value", None) for email in emails]
    users = UserModel.objects.filter(email__in=emails)
    if users.count() == 1:
        user = users.get()

        # We stored email instead of google UID in previous years, this backfills this data.
        if user.social_auth.exists():
            sa = user.social_auth.get()
            sa.uid = uid
            sa.save()
        return user
    else:
        return None


def get_user_pk_from_person_name(google_api_client, person_name) -> Optional[int]:
    cached_user_pk = cache.get(person_name, None)
    if cached_user_pk:
        return cached_user_pk
    else:
        uid = extract_id_from_person_name(person_name)
        user = get_puzzler_from_uid(google_api_client, uid) if uid else None
        if not user:
            return None
        cache.set(person_name, user.pk, timeout=None)
        return user.pk


def get_puzzle_pk_from_drive_item(drive_item_name) -> Optional[int]:
    cached_puzzle_pk = cache.get(drive_item_name, None)
    if cached_puzzle_pk:
        return cached_puzzle_pk

    drive_item_id = extract_id_from_drive_item_name(drive_item_name)
    if not drive_item_id:
        return None

    try:
        puzzle = Puzzle.objects.get(sheet__contains=drive_item_id)
        cache.set(drive_item_name, puzzle.pk, timeout=None)
        cache.set(puzzle.id, drive_item_name, timeout=None)
        return puzzle.pk
    except Puzzle.DoesNotExist:
        return None


def get_timestamp_from_activity(activity) -> Optional[datetime.datetime]:
    if "timestamp" in activity:
        timestamp = activity["timestamp"]
    elif "timeRange" in activity:
        timestamp = activity["timeRange"]["endTime"]
    else:
        return None

    # builtin datetime.datetime.fromisoformat should work in the future w/ python 3.11+
    return dateutil.parser.isoparse(timestamp)


@shared_task(base=GoogleApiClientTask, bind=True, time_limit=60)
def update_active_users(self, hunt_id):
    if not enabled():
        return

    hunt = Hunt.objects.select_related("settings").get(pk=hunt_id)

    if not hunt.settings.google_drive_folder_id:
        return

    now = datetime.datetime.now(tz=tz.UTC)

    if hunt.last_active_users_update_time:
        last_update_time = hunt.last_active_users_update_time
    else:
        last_update_time = hunt.start_time

    # avoid having to get and process too much data at once
    end = min(last_update_time + datetime.timedelta(minutes=10), now)

    if end > hunt.end_time:
        return

    action_filter = "detail.action_detail_case: EDIT"
    time_filter = "time > {} AND time <= {}".format(
        round(last_update_time.timestamp() * 1000), round(end.timestamp() * 1000)
    )

    body = {
        "filter": f"{action_filter} AND {time_filter}",
        "ancestorName": f"items/{hunt.settings.google_drive_folder_id}",
    }

    latest = {}
    while True:
        response = self.drive_activity_service().activity().query(body=body).execute()
        activities = response.get("activities", [])

        for activity in activities:
            users = [
                a["user"]["knownUser"]
                for a in activity["actors"]
                if "user" in a and "knownUser" in a["user"]
            ]
            drive_items = [
                t["driveItem"] for t in activity["targets"] if "driveItem" in t
            ]
            for user, drive_item in itertools.product(users, drive_items):
                user_pk = get_user_pk_from_person_name(self, user["personName"])
                if not user_pk:
                    continue
                puzzle_pk = get_puzzle_pk_from_drive_item(drive_item["name"])
                if not puzzle_pk:
                    continue

                timestamp = get_timestamp_from_activity(activity)

                if (user_pk, puzzle_pk) not in latest:
                    latest[(user_pk, puzzle_pk)] = (timestamp, 1)
                else:
                    (current_latest, num_edits) = latest[(user_pk, puzzle_pk)]
                    latest[(user_pk, puzzle_pk)] = (
                        max(timestamp, current_latest),
                        num_edits + 1,
                    )

        if "nextPageToken" not in response:
            break
        else:
            body["pageToken"] = response["nextPageToken"]

    with transaction.atomic():
        user_puzzle_pairs = [
            f"{user_pk}-{puzzle_pk}" for (user_pk, puzzle_pk) in latest.keys()
        ]
        old_activities = (
            PuzzleActivity.objects.annotate(
                user_puzzle_pair=Concat(
                    F("user_id"), Value("-"), F("puzzle_id"), output_field=CharField()
                )
            )
            .filter(user_puzzle_pair__in=user_puzzle_pairs)
            .select_for_update()
        )
        old_keys = [(e.user_id, e.puzzle_id) for e in old_activities]

        PuzzleActivity.objects.bulk_create(
            [
                PuzzleActivity(
                    puzzle_id=puzzle_pk,
                    user_id=user_pk,
                    last_edit_time=last_edit_time,
                    num_edits=num_edits,
                )
                for (
                    (user_pk, puzzle_pk),
                    (last_edit_time, num_edits),
                ) in latest.items()
                if (user_pk, puzzle_pk) not in old_keys
            ],
        )

        updates = []
        for activity in old_activities:
            (last_edit_time, num_edits) = latest[(activity.user_id, activity.puzzle_id)]
            activity.last_edit_time = last_edit_time
            activity.num_edits += num_edits
            updates.append(activity)

        if updates:
            PuzzleActivity.objects.bulk_update(
                updates, fields=["last_edit_time", "num_edits"]
            )

        hunt.last_active_users_update_time = end
        hunt.save()


@shared_task(base=GoogleApiClientTask, bind=True)
def get_file_user_emails(self, file_id) -> List[str]:
    """
    Returns a sorted list of emails that have access to `file_id` or None if the file is
    world readable.
    """
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
def sync_drive_permissions_for_hunt(self, hunt_id):
    if not enabled():
        return

    hunt = Hunt.objects.select_related("settings").get(pk=hunt_id)

    if not hunt.settings.google_drive_folder_id:
        return

    users_with_access = hunt.get_users_with_perm("hunt_access")

    UserModel = get_user_model()
    emails = get_file_user_emails.run(hunt.settings.google_drive_folder_id)
    if not emails:
        logger.warn("Unable to get Google Drive emails for hunt", hunt)
        return

    users = UserModel.objects.filter(email__in=emails).exclude(
        id__in=[user.pk for user in users_with_access]
    )
    assign_perm("hunt_access", users, hunt)
