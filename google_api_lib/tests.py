import datetime
from unittest.mock import MagicMock, patch

from django.test import TestCase

import google_api_lib
from accounts.models import Puzzler
from answers.models import Answer
from google_api_lib.utils import GoogleApiClientTask
from hunts.models import Hunt
from puzzles.models import Puzzle, PuzzleActivity

TEST_SHEET = "testsheet.com"
TEST_SHEET_TEMPLATE_ID = "12345abcde"

TEST_SHEET_EXISTING_FILE_ID = "a1s2d3f4"
TEST_SHEET_EXISTING_FILE_URL = "fakestuff.com"


def mock_create_google_sheets_helper(self, name, template_file_id):
    return {"id": "0", "webViewLink": TEST_SHEET}


def mock_transfer_ownership(file, new_owner):
    return


def mock_add_puzzle_link_to_sheet(puzzle_url, sheet_url):
    return


def mock_move_drive_file(file_id, destination_folder_id):
    return


def mock_maybe_get_renamable_sheet_for_puzzle(self, puzzle):
    return {
        "id": TEST_SHEET_EXISTING_FILE_ID,
        "webViewLink": TEST_SHEET_EXISTING_FILE_URL,
    }


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
        "google_api_lib.tasks.maybe_get_renamable_sheet_for_puzzle", lambda *args: None
    )
    @patch(
        "google_api_lib.tasks.add_puzzle_link_to_sheet", mock_add_puzzle_link_to_sheet
    )
    def test_sheet_creation_no_template_folder(self):
        puzzle = Puzzle.objects.create(
            name="test",
            hunt=self._test_hunt,
            url="fake_url.com",
            is_meta=False,
        )
        google_api_lib.tasks.create_google_sheets(puzzle.id)

        self.assertEqual(Puzzle.objects.get(pk=puzzle.id).sheet, TEST_SHEET)

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
        "google_api_lib.tasks.maybe_get_renamable_sheet_for_puzzle",
        mock_maybe_get_renamable_sheet_for_puzzle,
    )
    @patch(
        "google_api_lib.tasks.add_puzzle_link_to_sheet", mock_add_puzzle_link_to_sheet
    )
    def test_sheet_creation_with_template_folder(self):
        puzzle = Puzzle.objects.create(
            name="test",
            hunt=self._test_hunt,
            url="fake_url.com",
            is_meta=False,
        )
        google_api_lib.tasks.create_google_sheets(puzzle.id)

        self.assertEqual(
            Puzzle.objects.get(pk=puzzle.id).sheet, TEST_SHEET_EXISTING_FILE_URL
        )


def _drive_activity_response(timestamp):
    return {
        "activities": [
            {
                "timestamp": timestamp.isoformat(),
                "actors": [{"user": {"knownUser": {"personName": "people/1"}}}],
                "targets": [{"driveItem": {"name": "items/sheet1"}}],
            }
        ]
    }


class TestUpdateActiveUsers(TestCase):
    def setUp(self):
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        self._start = now - datetime.timedelta(hours=1)
        self._hunt = Hunt.objects.create(
            name="fake hunt",
            url="google.com",
            start_time=self._start,
            end_time=now + datetime.timedelta(hours=1),
        )
        self._hunt.settings.google_drive_folder_id = "folder"
        self._hunt.settings.save()
        self._user = Puzzler.objects.create_user(username="alice", password="pw")
        self._puzzle = Puzzle.objects.create(
            name="test", hunt=self._hunt, url="fake_url.com", is_meta=False
        )

    def _run(self):
        activity_service = MagicMock()
        activity_service.activity().query().execute.return_value = (
            _drive_activity_response(self._start + datetime.timedelta(minutes=5))
        )
        with (
            patch("google_api_lib.tasks.enabled", return_value=True),
            patch.object(
                GoogleApiClientTask,
                "drive_activity_service",
                return_value=activity_service,
            ),
            patch(
                "google_api_lib.tasks.get_user_pk_from_person_name",
                return_value=self._user.pk,
            ),
            patch(
                "google_api_lib.tasks.get_puzzle_pk_from_drive_item",
                return_value=self._puzzle.pk,
            ),
        ):
            google_api_lib.tasks.update_active_users(self._hunt.pk)

    def _activities(self):
        return PuzzleActivity.global_objects.filter(
            user=self._user, puzzle=self._puzzle
        )

    def _assert_watermark_advanced(self):
        self._hunt.refresh_from_db()
        self.assertIsNotNone(self._hunt.last_active_users_update_time)

    def _restore_puzzle(self):
        # strict=False matches the admin "Restore selected items" action.
        Puzzle.global_objects.get(pk=self._puzzle.pk).restore(strict=False)

    def test_new_activity_on_live_puzzle(self):
        self._run()

        self._assert_watermark_advanced()
        activity = PuzzleActivity.objects.get(user=self._user, puzzle=self._puzzle)
        self.assertEqual(activity.num_edits, 1)

    def test_edit_on_deleted_puzzle_updates_its_deleted_activity(self):
        # Soft-deleting a puzzle cascades to its activity rows. Those rows still
        # occupy the (user, puzzle) unique constraint, so re-creating the pair used
        # to raise IntegrityError and roll back without advancing the watermark,
        # killing active-user tracking for the whole hunt.
        PuzzleActivity.objects.create(
            user=self._user,
            puzzle=self._puzzle,
            last_edit_time=self._start,
            num_edits=3,
        )
        self._puzzle.delete()

        self._run()

        self._assert_watermark_advanced()
        activity = self._activities().get()
        self.assertTrue(activity.is_deleted)
        self.assertEqual(activity.num_edits, 4)

        self._restore_puzzle()
        activity = PuzzleActivity.objects.get(user=self._user, puzzle=self._puzzle)
        self.assertEqual(activity.num_edits, 4)

    def test_first_edit_on_deleted_puzzle_is_restored_with_it(self):
        self._puzzle.delete()

        self._run()

        self._assert_watermark_advanced()
        activity = self._activities().get()
        self.assertTrue(activity.is_deleted)

        self._restore_puzzle()
        activity = PuzzleActivity.objects.get(user=self._user, puzzle=self._puzzle)
        self.assertEqual(activity.num_edits, 1)

    def test_edit_updates_individually_deleted_activity(self):
        # e.g. an admin deleted the activity row directly; the puzzle is live.
        PuzzleActivity.objects.create(
            user=self._user,
            puzzle=self._puzzle,
            last_edit_time=self._start,
            num_edits=3,
        ).delete()

        self._run()

        self._assert_watermark_advanced()
        activity = self._activities().get()
        self.assertEqual(activity.num_edits, 4)


@patch("google_api_lib.tasks.maybe_get_renamable_sheet_for_puzzle", lambda *args: None)
@patch("google_api_lib.tasks.transfer_ownership.delay")
@patch("google_api_lib.tasks.add_puzzle_link_to_sheet.delay")
@patch("google_api_lib.tasks.move_drive_file.delay")
@patch("google_api_lib.tasks.rename_sheet.delay")
class TestSheetCreationRaces(TestCase):
    """The Drive copy takes seconds; edits made meanwhile must survive the task."""

    def setUp(self):
        self._hunt = Hunt.objects.create(name="fake hunt", url="google.com")
        self._hunt.settings.google_sheets_template_file_id = TEST_SHEET_TEMPLATE_ID
        self._hunt.settings.save()
        self._puzzle = Puzzle.objects.create(
            name="orig", hunt=self._hunt, url="fake_url.com", is_meta=False
        )

    def _create_sheet(self, during_copy=None):
        def copy(task, name, template_file_id):
            if during_copy:
                during_copy()
            return mock_create_google_sheets_helper(task, name, template_file_id)

        with patch("google_api_lib.tasks.create_google_sheets_helper", copy):
            with self.captureOnCommitCallbacks(execute=True):
                google_api_lib.tasks.create_google_sheets(self._puzzle.id)

    def test_edits_during_copy_are_kept_and_retitle_the_sheet(self, rename_sheet, *_):
        def edit():
            puzzle = Puzzle.objects.get(pk=self._puzzle.pk)
            puzzle.name = "renamed"
            puzzle.notes = "my notes"
            puzzle.status = Puzzle.SOLVED
            puzzle.answer = "ANS"
            puzzle.save()
            Answer.objects.create(text="ANS", puzzle=puzzle, status=Answer.CORRECT)

        self._create_sheet(during_copy=edit)

        puzzle = Puzzle.objects.get(pk=self._puzzle.pk)
        self.assertEqual(puzzle.sheet, TEST_SHEET)
        self.assertEqual(puzzle.name, "renamed")
        self.assertEqual(puzzle.notes, "my notes")
        self.assertEqual(puzzle.status, Puzzle.SOLVED)
        self.assertEqual(puzzle.answer, "ANS")
        # The rename view saw no sheet yet, so the task must retitle it.
        rename_sheet.assert_called_once_with(TEST_SHEET, "[SOLVED: ANS] renamed")

    def test_no_rename_when_nothing_changed_during_copy(self, rename_sheet, *_):
        self._create_sheet()

        self.assertEqual(Puzzle.objects.get(pk=self._puzzle.pk).sheet, TEST_SHEET)
        rename_sheet.assert_not_called()

    def test_delete_during_copy_is_not_undone(self, rename_sheet, *_):
        self._create_sheet(
            during_copy=lambda: Puzzle.objects.get(pk=self._puzzle.pk).delete()
        )

        self.assertFalse(Puzzle.objects.filter(pk=self._puzzle.pk).exists())
        puzzle = Puzzle.global_objects.get(pk=self._puzzle.pk)
        self.assertEqual(puzzle.sheet, TEST_SHEET)
        rename_sheet.assert_called_once_with(TEST_SHEET, "[DELETED] orig")
