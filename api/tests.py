from unittest.mock import patch

from django.conf import settings
from django.test import TransactionTestCase, override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

import google_api_lib
import google_api_lib.tests
from puzzles.models import Puzzle
from puzzles.puzzle_tag import LOCATION_COLOR, META_COLOR, PuzzleTag, PuzzleTagColor

from .test_helpers import CardboardTestCase

TEST_URL = "https://cardboard.test/"
TEST_NAME = "Test"
META_URL = "https://thisisameta.puzzle"
META_NAME = "Meta"


# Disable all chat features for the purposes of this unit test.
@override_settings(
    CHAT_DEFAULT_SERVICE=None,
    CHAT_SERVICES={},
)
class ApiTests(CardboardTestCase, APITestCase):
    def test_get_hunt(self):
        response = self.get_hunt()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "id": self._hunt.pk,
                "name": self._hunt.name,
                "url": self._hunt.url,
                "active": self._hunt.active,
                "has_drive": bool(self._hunt.settings.google_drive_human_url),
                "puzzle_tags": [],
                "create_channel_by_default": self._hunt.settings.create_channel_by_default,
            },
        )

    def test_get_hunt_permissions(self):
        self.set_permissions_level(can_access=False)
        self.check_response_status(self.get_hunt(), status.HTTP_403_FORBIDDEN)

    def test_create_invalid_puzzle(self):
        # Missing name
        self.check_response_status(
            self.create_puzzle({"url": TEST_URL, "is_meta": False}),
            status.HTTP_400_BAD_REQUEST,
        )

        # Missing url
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "is_meta": False}),
            status.HTTP_400_BAD_REQUEST,
        )

        # Empty string name
        self.check_response_status(
            self.create_puzzle({"name": "", "url": TEST_URL, "is_meta": False}),
            status.HTTP_400_BAD_REQUEST,
        )

        # Malformatted URL (TODO)
        # response = self.create_puzzle(
        #     {"name": TEST_NAME, "url": "bad_url", "is_meta": False}
        # )
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Puzzle.objects.count(), 0)

    def test_create_puzzle(self):
        response = self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        puzzle = Puzzle.objects.get()
        self.assertEqual(
            response.data,
            {
                "id": puzzle.pk,
                "name": puzzle.name,
                "hunt_id": self._hunt.pk,
                "url": TEST_URL,
                "notes": "",
                "has_sheet": False,
                "chat_room": None,
                "status": "SOLVING",
                "tags": [],
                "guesses": [],
                "metas": [],
                "feeders": [],
                "is_meta": False,
                "created_on": puzzle.created_on.astimezone(
                    timezone.get_current_timezone()
                ).isoformat(),
                "last_edited_on": None,
                "recent_editors": [],
                "top_editors": [],
            },
        )

    def test_create_puzzle_permissions(self):
        self.set_permissions_level(can_access=False)
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "url": TEST_URL}),
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(Puzzle.objects.count(), 0)

    def test_create_puzzle_with_meta_assigned(self):
        # Add meta
        meta_response = self.create_puzzle(
            {"name": META_NAME, "url": META_URL, "is_meta": True}
        )
        self.assertEqual(meta_response.status_code, status.HTTP_200_OK)
        meta_id = meta_response.data["id"]
        response = self.create_puzzle(
            {"name": TEST_NAME, "url": TEST_URL, "assigned_meta": META_NAME}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        puzzle = Puzzle.objects.get(is_meta=False)
        self.assertEqual(response.data["metas"], [meta_id])

    def test_delete_puzzle(self):
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        )
        puzzle = Puzzle.objects.get()
        response = self.delete_puzzle(puzzle.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})
        self.assertEqual(Puzzle.objects.count(), 0)

    def test_delete_puzzle_permissions(self):
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        )
        puzzle = Puzzle.objects.get()

        self.set_permissions_level(can_access=False)

        response = self.delete_puzzle(puzzle.pk)
        self.check_response_status(
            self.delete_puzzle(puzzle.pk), status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(Puzzle.objects.count(), 1)

    def test_edit_puzzle(self):
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        )
        puzzle = Puzzle.objects.get()

        response = self.edit_puzzle(puzzle.pk, {"name": TEST_NAME + "2"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], TEST_NAME + "2")
        puzzle.refresh_from_db()
        self.assertEqual(puzzle.name, TEST_NAME + "2")

        response = self.edit_puzzle(puzzle.pk, {"url": "https://newurl.test/"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["url"], "https://newurl.test/")
        puzzle.refresh_from_db()
        self.assertEqual(puzzle.url, "https://newurl.test/")

        response = self.edit_puzzle(puzzle.pk, {"is_meta": True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["is_meta"], True)
        self.assertEqual(len(response.data["tags"]), 1)
        puzzle.refresh_from_db()
        self.assertEqual(puzzle.is_meta, True)

    def test_edit_puzzle_permissions(self):
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        )
        puzzle = Puzzle.objects.get()

        self.set_permissions_level(can_access=False)

        self.check_response_status(
            self.edit_puzzle(puzzle.pk, {"name": TEST_NAME + "2"}),
            status.HTTP_403_FORBIDDEN,
        )
        puzzle.refresh_from_db()
        self.assertEqual(puzzle.name, TEST_NAME)

    def test_list_puzzles(self):
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        )
        self.check_response_status(
            self.create_puzzle(
                {"name": "second test", "url": "https://secondtest.test/"}
            )
        )
        self.assertEqual(Puzzle.objects.count(), 2)
        response = self.list_puzzles()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual({p["name"] for p in response.data}, {TEST_NAME, "second test"})

    def test_list_puzzles_permissions(self):
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        )

        self.set_permissions_level(can_access=False)

        self.check_response_status(
            self.list_puzzles(),
            status.HTTP_403_FORBIDDEN,
        )

    def test_add_answer(self):
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        )
        puzzle = Puzzle.objects.get()

        self.check_response_status(self.create_answer(puzzle.pk, {"text": "ans"}))
        # This assumes no answer queue
        puzzle.refresh_from_db()
        self.assertEqual(puzzle.correct_answers(), ["ANS"])
        self.assertEqual(puzzle.status, Puzzle.SOLVED)

        self.check_response_status(
            self.create_answer(puzzle.pk, {"text": "ans"}), status.HTTP_400_BAD_REQUEST
        )
        self.check_response_status(
            self.create_answer(puzzle.pk, {"text": ""}), status.HTTP_400_BAD_REQUEST
        )
        self.check_response_status(
            self.create_answer(puzzle.pk, {"text": "answer two"})
        )

        puzzle.refresh_from_db()
        self.assertEqual(puzzle.correct_answers(), ["ANS", "ANSWERTWO"])

    def test_add_answer_permissions(self):
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        )
        puzzle = Puzzle.objects.get()

        self.set_permissions_level(can_access=False)
        self.check_response_status(
            self.create_answer(puzzle.pk, {"text": "ans"}),
            status.HTTP_403_FORBIDDEN,
        )
        puzzle.refresh_from_db()
        self.assertEqual(puzzle.correct_answers(), [])
        self.assertEqual(puzzle.status, Puzzle.SOLVING)

    def test_delete_answer(self):
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        )
        puzzle = Puzzle.objects.get()

        self.check_response_status(self.create_answer(puzzle.pk, {"text": "ANSWER"}))
        self.check_response_status(
            self.create_answer(puzzle.pk, {"text": "ANSWER TWO"})
        )

        puzzle.refresh_from_db()
        self.assertEqual(puzzle.status, Puzzle.SOLVED)
        self.assertEqual(len(puzzle.correct_answers()), 2)
        guesses = list(puzzle.guesses.all())

        self.check_response_status(self.delete_answer(puzzle.pk, guesses[0].pk))
        puzzle.refresh_from_db()
        self.assertEqual(puzzle.status, Puzzle.SOLVED)
        self.assertEqual(len(puzzle.correct_answers()), 1)

        self.check_response_status(self.delete_answer(puzzle.pk, guesses[1].pk))
        puzzle.refresh_from_db()
        self.assertEqual(puzzle.status, Puzzle.SOLVING)
        self.assertEqual(len(puzzle.correct_answers()), 0)

    def test_delete_answer_permissions(self):
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        )
        puzzle = Puzzle.objects.get()
        self.check_response_status(
            self.create_answer(puzzle.pk, {"text": "ans"}),
        )
        puzzle.refresh_from_db()
        self.assertEqual(puzzle.status, Puzzle.SOLVED)
        self.assertEqual(len(puzzle.correct_answers()), 1)
        guesses = list(puzzle.guesses.all())

        self.set_permissions_level(can_access=False)
        self.check_response_status(
            self.delete_answer(puzzle.pk, guesses[0].pk), status.HTTP_403_FORBIDDEN
        )
        puzzle.refresh_from_db()
        self.assertEqual(puzzle.status, Puzzle.SOLVED)
        self.assertEqual(len(puzzle.correct_answers()), 1)

    def test_edit_answer(self):
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        )
        puzzle = Puzzle.objects.get()

        self.check_response_status(self.create_answer(puzzle.pk, {"text": "ANSWER"}))
        answer = puzzle.guesses.get()

        self.check_response_status(
            self.edit_answer(puzzle.pk, answer.pk, {"text": "oops real answer"})
        )
        answer.refresh_from_db()
        self.assertEqual(answer.text, "OOPSREALANSWER")

    def test_edit_answer_permissions(self):
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        )
        puzzle = Puzzle.objects.get()

        self.check_response_status(self.create_answer(puzzle.pk, {"text": "ANSWER"}))
        answer = puzzle.guesses.get()

        self.set_permissions_level(can_access=False)
        self.check_response_status(
            self.edit_answer(puzzle.pk, answer.pk, {"text": "oops real answer"}),
            status.HTTP_403_FORBIDDEN,
        )
        answer.refresh_from_db()
        self.assertEqual(answer.text, "ANSWER")

    def test_create_tag(self):
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        )
        puzzle = Puzzle.objects.get()

        response = self.create_tag(
            puzzle.pk, {"name": "taggy", "color": PuzzleTagColor.BLUE}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(puzzle.tags.count(), 1)
        # Should return a puzzle
        self.assertEqual(response.data[0]["name"], puzzle.name)

    def test_create_tag_permissions(self):
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        )
        puzzle = Puzzle.objects.get()

        self.set_permissions_level(can_access=False)
        self.check_response_status(
            self.create_tag(puzzle.pk, {"name": "taggy", "color": PuzzleTagColor.BLUE}),
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(puzzle.tags.count(), 0)

    def test_create_location_tag(self):
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        )
        puzzle = Puzzle.objects.get()
        response = self.create_tag(
            puzzle.pk, {"name": "location", "color": LOCATION_COLOR}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(puzzle.tags.count(), 1)
        self.assertTrue(puzzle.tags.first().is_location)

    def test_delete_tag(self):
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        )
        puzzle = Puzzle.objects.get()
        self.check_response_status(
            self.create_tag(puzzle.pk, {"name": "taggy", "color": PuzzleTagColor.BLUE})
        )
        self.assertEqual(puzzle.tags.count(), 1)
        tag = puzzle.tags.get()

        self.check_response_status(self.delete_tag(puzzle.pk, tag.pk))
        self.assertEqual(puzzle.tags.count(), 0)

    def test_delete_tag_permissions(self):
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        )
        puzzle = Puzzle.objects.get()
        self.check_response_status(
            self.create_tag(puzzle.pk, {"name": "taggy", "color": PuzzleTagColor.BLUE})
        )
        self.assertEqual(puzzle.tags.count(), 1)
        tag = puzzle.tags.get()

        self.set_permissions_level(can_access=False)
        self.check_response_status(
            self.delete_tag(puzzle.pk, tag.pk), status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(puzzle.tags.count(), 1)

    def test_can_delete_same_name_tag(self):
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        )
        puzzle = Puzzle.objects.get()
        self.check_response_status(
            self.create_tag(
                puzzle.pk, {"name": TEST_NAME, "color": PuzzleTagColor.BLUE}
            )
        )
        self.assertEqual(puzzle.tags.count(), 1)
        tag = puzzle.tags.get()

        self.check_response_status(self.delete_tag(puzzle.pk, tag.pk))
        self.assertEqual(puzzle.tags.count(), 0)

    def test_cannot_delete_meta_tag(self):
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "url": TEST_URL, "is_meta": True})
        )
        puzzle = Puzzle.objects.get()
        self.assertEqual(puzzle.tags.count(), 1)
        tag = puzzle.tags.get()

        self.check_response_status(
            self.delete_tag(puzzle.pk, tag.pk), status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(puzzle.tags.count(), 1)

    def test_opposing_tags(self):
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        )
        puzzle = Puzzle.objects.get()
        self.check_response_status(
            self.create_tag(
                puzzle.pk,
                {"name": PuzzleTag.HIGH_PRIORITY, "color": PuzzleTagColor.RED},
            )
        )
        self.assertEqual(puzzle.tags.count(), 1)
        tag = puzzle.tags.get()
        self.assertEqual(tag.name, PuzzleTag.HIGH_PRIORITY)

        response = self.create_tag(
            puzzle.pk, {"name": PuzzleTag.LOW_PRIORITY, "color": PuzzleTagColor.YELLOW}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should still have only 1 tag.
        self.assertEqual(puzzle.tags.count(), 1)
        self.assertEqual(puzzle.tags.all()[0].name, PuzzleTag.LOW_PRIORITY)
        # Should return a puzzle
        self.assertEqual(response.data[0]["name"], puzzle.name)

    def test_cannot_change_meta_tag_color(self):
        meta_puzzle_name = "test meta"
        self.check_response_status(
            self.create_puzzle(
                {
                    "name": meta_puzzle_name,
                    "url": "{}/meta".format(TEST_URL),
                    "is_meta": True,
                }
            )
        )
        self.check_response_status(
            self.create_puzzle(
                {
                    "name": TEST_NAME,
                    "url": "{}/puzzle".format(TEST_URL),
                    "is_meta": False,
                }
            )
        )
        meta = Puzzle.objects.get(is_meta=True)
        puzzle = Puzzle.objects.get(is_meta=False)

        self.check_response_status(
            self.create_tag(
                puzzle.pk, {"name": meta.name, "color": PuzzleTagColor.BLUE}
            )
        )
        self.assertEqual(puzzle.tags.count(), 1)

        meta_tag = puzzle.tags.get(name=meta.name)
        self.assertEqual(meta_tag.color, META_COLOR)

    def test_empty_custom_tags_deletion(self):
        # test that a empty custom tag is reaped
        self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        puzzle = Puzzle.objects.get()
        custom_tag = PuzzleTag.objects.create(
            name="custom", hunt=self._hunt, is_default=False
        )
        puzzle.tags.add(custom_tag)
        self.client.delete(
            f"/api/v1/puzzles/{puzzle.pk}/tags/{custom_tag.pk}",
        )
        self.assertFalse(
            PuzzleTag.objects.filter(hunt=self._hunt, name="custom").exists()
        )

    def test_empty_default_tags_deletion(self):
        # test that a empty default tag is NOT reaped
        self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        puzzle = Puzzle.objects.get()
        PuzzleTag.create_default_tags(self._hunt)

        for tag in PuzzleTag.objects.filter(is_default=True):
            puzzle.tags.add(tag)

            self.client.delete(
                f"/api/v1/puzzles/{puzzle.pk}/tags/{tag.pk}",
            )

        for name, color in PuzzleTag.DEFAULT_TAGS:
            self.assertTrue(
                PuzzleTag.objects.filter(
                    hunt=self._hunt, name=name, color=color
                ).exists()
            )


@override_settings(
    CHAT_DEFAULT_SERVICE=None,
    CHAT_SERVICES={},
)
class SheetTests(CardboardTestCase, TransactionTestCase):
    @patch("google_api_lib.tasks.rename_sheet.delay")
    @patch(
        "google_api_lib.tasks.create_google_sheets_helper",
        google_api_lib.tests.mock_create_google_sheets_helper,
    )
    @patch(
        "google_api_lib.tasks.transfer_ownership.delay",
        google_api_lib.tests.mock_transfer_ownership,
    )
    @patch(
        "google_api_lib.tasks.add_puzzle_link_to_sheet.delay",
        google_api_lib.tests.mock_add_puzzle_link_to_sheet,
    )
    def test_sheets_title_editing(self, rename_sheet):
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        )
        puzzle = Puzzle.objects.get()
        google_api_lib.tasks.create_google_sheets(puzzle.id)

        with override_settings(GOOGLE_API_AUTHN_INFO={}):
            self.check_response_status(self.create_answer(puzzle.pk, {"text": "ans"}))
            rename_sheet.assert_called_with(
                sheet_url=google_api_lib.tests.TEST_SHEET,
                name=f"[SOLVED: ANS] {puzzle.name}",
            )

            self.check_response_status(self.create_answer(puzzle.pk, {"text": "ans2"}))
            rename_sheet.assert_called_with(
                sheet_url=google_api_lib.tests.TEST_SHEET,
                name=f"[SOLVED: ANS, ANS2] {puzzle.name}",
            )

            self.check_response_status(
                self.create_tag(
                    puzzle.pk, {"name": "BACKSOLVED", "color": PuzzleTagColor.GREEN}
                )
            )
            rename_sheet.assert_called_with(
                sheet_url=google_api_lib.tests.TEST_SHEET,
                name=f"[BACKSOLVED: ANS, ANS2] {puzzle.name}",
            )

            self.check_response_status(
                self.delete_answer(puzzle.pk, puzzle.guesses.get(text="ANS").pk)
            )
            rename_sheet.assert_called_with(
                sheet_url=google_api_lib.tests.TEST_SHEET,
                name=f"[BACKSOLVED: ANS2] {puzzle.name}",
            )

            self.check_response_status(
                self.delete_answer(puzzle.pk, puzzle.guesses.get(text="ANS2").pk)
            )
            rename_sheet.assert_called_with(
                sheet_url=google_api_lib.tests.TEST_SHEET, name=f"{puzzle.name}"
            )

    @patch("google_api_lib.tasks.rename_sheet.delay")
    @patch(
        "google_api_lib.tasks.create_google_sheets_helper",
        google_api_lib.tests.mock_create_google_sheets_helper,
    )
    @patch(
        "google_api_lib.tasks.transfer_ownership.delay",
        google_api_lib.tests.mock_transfer_ownership,
    )
    @patch(
        "google_api_lib.tasks.add_puzzle_link_to_sheet.delay",
        google_api_lib.tests.mock_add_puzzle_link_to_sheet,
    )
    def test_sheets_title_editing_case_insensitive(self, rename_sheet):
        self.check_response_status(
            self.create_puzzle({"name": TEST_NAME, "url": TEST_URL})
        )
        puzzle = Puzzle.objects.get()
        google_api_lib.tasks.create_google_sheets(puzzle.id)

        with override_settings(GOOGLE_API_AUTHN_INFO={}):
            self.check_response_status(self.create_answer(puzzle.pk, {"text": "ans"}))
            rename_sheet.assert_called_with(
                sheet_url=google_api_lib.tests.TEST_SHEET,
                name=f"[SOLVED: ANS] {puzzle.name}",
            )

            self.check_response_status(self.create_answer(puzzle.pk, {"text": "ans2"}))
            rename_sheet.assert_called_with(
                sheet_url=google_api_lib.tests.TEST_SHEET,
                name=f"[SOLVED: ANS, ANS2] {puzzle.name}",
            )

            self.check_response_status(
                self.create_tag(
                    puzzle.pk, {"name": "backSoLvEd", "color": PuzzleTagColor.GREEN}
                )
            )
            rename_sheet.assert_called_with(
                sheet_url=google_api_lib.tests.TEST_SHEET,
                name=f"[BACKSOLVED: ANS, ANS2] {puzzle.name}",
            )

            self.check_response_status(
                self.delete_answer(puzzle.pk, puzzle.guesses.get(text="ANS").pk)
            )
            rename_sheet.assert_called_with(
                sheet_url=google_api_lib.tests.TEST_SHEET,
                name=f"[BACKSOLVED: ANS2] {puzzle.name}",
            )

            self.check_response_status(
                self.delete_answer(puzzle.pk, puzzle.guesses.get(text="ANS2").pk)
            )
            rename_sheet.assert_called_with(
                sheet_url=google_api_lib.tests.TEST_SHEET, name=f"{puzzle.name}"
            )
