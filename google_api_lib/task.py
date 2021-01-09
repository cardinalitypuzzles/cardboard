import httplib2
import logging
import os

from django.conf import settings

from googleapiclient import _auth

from celery import shared_task
from .utils import GoogleApiClientTask
from puzzles.models import Puzzle

logger = logging.getLogger(__name__)


# helper function that can be mocked for testing
def create_google_sheets_helper(self, name):
    req_body = {"name": name}
    # copy template sheet
    file = (
        self.drive_service()
        .files()
        .copy(
            fileId=settings.GOOGLE_SHEETS_TEMPLATE_FILE_ID,
            body=req_body,
            fields="id,webViewLink,permissions",
        )
        .execute()
    )
    return file


# transfer new sheet ownership back to OG owner, so that scripts can run
@shared_task(base=GoogleApiClientTask, bind=True)
def transfer_ownership(self, file):
    permission = next(
        p for p in file["permissions"] if p["emailAddress"] == self._sheets_owner
    )
    self.drive_service().permissions().update(
        fileId=file["id"],
        permissionId=permission["id"],
        body={"role": "owner"},
        transferOwnership=True,
    ).execute()


@shared_task(base=GoogleApiClientTask, bind=True)
def create_google_sheets(self, puzzle_id, name, puzzle_url=None):
    response = create_google_sheets_helper(self, name)
    sheet_url = response["webViewLink"]
    if puzzle_url:
        add_puzzle_link_to_sheet(puzzle_url, sheet_url)
    puzzle = Puzzle.objects.filter(pk=puzzle_id).update(sheet=sheet_url)
    transfer_ownership.delay(response)
    return sheet_url


def extract_id_from_sheets_url(url):
    """
    Assumes `url` is of the form
    https://docs.google.com/spreadsheets/d/<ID>/edit...
    and returns the <ID> portion
    """
    start = url.find("/d/") + 3
    end = url.find("/edit")
    return url[start:end]


@shared_task(base=GoogleApiClientTask, bind=True)
def add_puzzle_link_to_sheet(self, puzzle_url, sheet_url):
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


@shared_task(base=GoogleApiClientTask, bind=True, rate_limit="1/m")
def update_meta_sheet_feeders(self, puzzle_id):
    """
    Updates the input meta puzzle's spreadsheet with the
    latest feeder puzzle info
    """
    meta_puzzle = Puzzle.objects.get(pk=puzzle_id)
    if not meta_puzzle.is_meta:
        return

    # TODO(erwa): Use work queue and separate process for running tasks.
    # See https://github.com/cardinalitypuzzles/smallboard/pull/140
    # for discussion. Need to use locking to prevent race conditions
    # if there is more than one worker thread/process.

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
    response = (
        self.sheets_service()
        .spreadsheets()
        .get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties.title,sheets.properties.sheetId",
        )
        .execute(http=http)
    )

    requests = []
    for sheet in response["sheets"]:
        if sheet["properties"]["title"] == "AUTOGENERATED":
            requests.append(
                {"deleteSheet": {"sheetId": sheet["properties"]["sheetId"]}}
            )
            break
    requests.append(
        {
            "addSheet": {
                "properties": {
                    "title": "AUTOGENERATED",
                },
            },
        }
    )
    response = (
        self.sheets_service()
        .spreadsheets()
        .batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests},
            fields="replies.addSheet.properties.sheetId",
        )
        .execute(http=http)
    )
    sheet_id = response["replies"][-1]["addSheet"]["properties"]["sheetId"]

    def __get_answer_or_blank(puzzle, i):
        if i < len(feeders_to_answers[puzzle]):
            return feeders_to_answers[puzzle][i]
        return ""

    body = {
        "requests": [
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
                                        "stringValue": "DO NOT MAKE CHANGES HERE; COPY INFO TO ANOTHER SHEET FIRST."
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
                                    "userEnteredValue": {"stringValue": "Puzzle Name"},
                                    "userEnteredFormat": {"textFormat": {"bold": True}},
                                },
                                {
                                    "userEnteredValue": {"stringValue": "Sheet"},
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
                                {"userEnteredValue": {"stringValue": puzzle.name}},
                                {
                                    "userEnteredValue": {
                                        "formulaValue": '=HYPERLINK("%s", "sheet")'
                                        % puzzle.sheet
                                    }
                                },
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
    }
    self.sheets_service().spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body=body
    ).execute(http=http)
    logger.info(
        "Done updating the meta sheet for '%s' " "with feeder puzzles" % meta_puzzle
    )
