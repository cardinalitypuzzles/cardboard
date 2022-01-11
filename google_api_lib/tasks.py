import logging
import random

from django.conf import settings
from django.db import transaction

from googleapiclient import _auth

from celery import shared_task
from chat.tasks import handle_sheet_created
from .utils import GoogleApiClientTask
from cardboard.settings import TaskPriority
from puzzles.models import Puzzle

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
        body={"role": "owner"},
        transferOwnership=True,
    ).execute()


@shared_task(base=GoogleApiClientTask, bind=True, priority=TaskPriority.HIGH.value)
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
            [f'=HYPERLINK("{puzzle_url}", "{puzzle_url}")'],
        ]
    }
    self.sheets_service().spreadsheets().values().update(
        spreadsheetId=extract_id_from_sheets_url(sheet_url),
        range="B2:C3",
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
def __add_sheet(sheets_service, http, spreadsheet_id, title) -> str:
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


def __clear_sheet(sheets_service, http, spreadsheet_id, sheet_id) -> None:
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


@shared_task(base=GoogleApiClientTask, bind=True, priority=TaskPriority.LOW.value)
def update_meta_sheet_feeders(self, puzzle_id) -> None:
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
    feeders_to_answers = {f: f.correct_answers() for f in feeders}

    if len(feeders_to_answers) > 0:
        max_num_answers = max(1, max((len(v) for v in feeders_to_answers.values())))
    else:
        max_num_answers = 1

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
        if sheet["properties"]["title"] == "AUTOGENERATED":
            sheet_id = sheet["properties"]["sheetId"]
            if "protectedRanges" in sheet and len(sheet["protectedRanges"]) > 0:
                protected_range_id = sheet["protectedRanges"][0]["protectedRangeId"]
            break

    if sheet_id is None:
        # create AUTOGENERATED tab if it does not exist
        sheet_id = __add_sheet(sheets_service, http, spreadsheet_id, "AUTOGENERATED")
    else:
        # otherwise, clear the sheet
        __clear_sheet(sheets_service, http, spreadsheet_id, sheet_id)

    def __get_answer_or_blank(puzzle, i):
        if i < len(feeders_to_answers[puzzle]):
            return feeders_to_answers[puzzle][i]
        return ""

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
                    "endRowIndex": 4 + len(feeders),
                    "startColumnIndex": 0,
                    "endColumnIndex": 3 + max_num_answers,
                },
                "rows": [
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
                            {
                                "userEnteredValue": {
                                    "stringValue": "COPY INFO TO ANOTHER SHEET."
                                }
                            }
                        ]
                    },
                    {},
                    {
                        "values": [
                            {
                                "userEnteredValue": {"stringValue": "Puzzle Link"},
                                "userEnteredFormat": {"textFormat": {"bold": True}},
                            },
                            {
                                "userEnteredValue": {"stringValue": "Sheet"},
                                "userEnteredFormat": {"textFormat": {"bold": True}},
                            },
                            {
                                "userEnteredValue": {"stringValue": "Puzzle Name"},
                                "userEnteredFormat": {"textFormat": {"bold": True}},
                            },
                        ]
                        + [
                            {
                                "userEnteredValue": {"stringValue": "Answer"},
                                "userEnteredFormat": {"textFormat": {"bold": True}},
                            },
                        ]
                        * max_num_answers
                    },
                ]
                + [
                    {
                        "values": [
                            {
                                "userEnteredValue": {
                                    "formulaValue": '=HYPERLINK("%s", "puzzle")'
                                    % puzzle.url
                                }
                            },
                            {
                                "userEnteredValue": {
                                    "formulaValue": '=HYPERLINK("%s", "sheet")'
                                    % puzzle.sheet
                                }
                            },
                            {"userEnteredValue": {"stringValue": puzzle.name}},
                        ]
                        + [
                            {
                                "userEnteredValue": {
                                    "stringValue": __get_answer_or_blank(puzzle, i)
                                },
                                "userEnteredFormat": {
                                    "textFormat": {"fontFamily": "Roboto Mono"}
                                },
                            }
                            for i in range(max_num_answers)
                        ]
                    }
                    for puzzle in feeders
                ],
            },
        },
        {
            "autoResizeDimensions": {
                "dimensions": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 1,
                    "endIndex": 3,
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
