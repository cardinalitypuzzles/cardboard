from django.test import TestCase
from unittest.mock import patch
from hunts.models import Hunt
from puzzles.models import Puzzle
import google_api_lib

TEST_SHEET = "testsheet.com"
TEST_SHEET_TEMPLATE_ID = "12345abcde"


def mock_create_google_sheets_helper(self, name, template_file_id):
    return {"id": "0", "webViewLink": TEST_SHEET}


def mock_transfer_ownership(file, new_owner):
    return


def mock_add_puzzle_link_to_sheet(puzzle_url, sheet_url):
    return


def mock_move_drive_file(file_id, destination_folder_id):
    return


class TestGoogleSheets(TestCase):
    def setUp(self):
        self.client.login(username="test", password="testingpwd")
        self._test_hunt = Hunt.objects.create(name="fake hunt", url="google.com")

        self._test_hunt.settings.google_sheets_template_file_id = TEST_SHEET_TEMPLATE_ID
        self._test_hunt.settings.save()

    def tearDown(self):
        self._test_hunt.delete()

    @patch(
        "google_api_lib.tasks.create_google_sheets_helper",
        mock_create_google_sheets_helper,
    )
    @patch(
        "google_api_lib.tasks.transfer_ownership.delay",
        mock_transfer_ownership,
    )
    @patch("google_api_lib.tasks.move_drive_file.delay", mock_move_drive_file)
    @patch(
        "google_api_lib.tasks.add_puzzle_link_to_sheet", mock_add_puzzle_link_to_sheet
    )
    def test_sheet_creation(self):
        puzzle = Puzzle.objects.create(
            name="test",
            hunt=self._test_hunt,
            url="fake_url.com",
            is_meta=False,
        )
        google_api_lib.tasks.create_google_sheets(puzzle.id)

        self.assertEqual(Puzzle.objects.get(pk=puzzle.id).sheet, TEST_SHEET)
