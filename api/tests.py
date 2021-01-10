from .test_helpers import SmallboardTestCase
from django.test import override_settings
from rest_framework import status
from puzzles.models import Puzzle, PuzzleTag

TEST_URL = "https://smallboard.test/"


# Disable all chat features for the purposes of this unit test.
@override_settings(
    CHAT_DEFAULT_SERVICE=None,
    CHAT_SERVICES={},
)
class ApiTests(SmallboardTestCase):
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
            },
        )

    def test_create_invalid_puzzle(self):
        # Missing name
        response = self.create_puzzle(
            {"url": "https://smallboard.test", "is_meta": False}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Missing url
        response = self.create_puzzle({"name": "test name", "is_meta": False})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Empty string name
        response = self.create_puzzle({"name": "", "url": TEST_URL, "is_meta": False})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Malformatted URL (TODO)
        # response = self.create_puzzle(
        #     {"name": "test name", "url": "bad_url", "is_meta": False}
        # )
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Puzzle.objects.count(), 0)

    def test_create_puzzle(self):
        response = self.create_puzzle({"name": "test name", "url": TEST_URL})
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
                "sheet": None,
                "chat_room": {},
                "status": "SOLVING",
                "tags": [],
                "guesses": [],
                "metas": [],
                "feeders": [],
                "is_meta": False,
            },
        )

    def test_delete_puzzle(self):
        self.create_puzzle({"name": "test name", "url": TEST_URL})
        puzzle = Puzzle.objects.get()
        response = self.delete_puzzle(puzzle.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})
        self.assertEqual(Puzzle.objects.count(), 0)

    def test_edit_puzzle(self):
        self.create_puzzle({"name": "test name", "url": TEST_URL})
        puzzle = Puzzle.objects.get()

        response = self.edit_puzzle(puzzle.pk, {"name": "new name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "new name")
        puzzle.refresh_from_db()
        self.assertEqual(puzzle.name, "new name")

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

    def test_list_puzzles(self):
        self.create_puzzle({"name": "test name", "url": TEST_URL})
        self.create_puzzle({"name": "second test", "url": "https://secondtest.test/"})
        self.assertEqual(Puzzle.objects.count(), 2)
        response = self.list_puzzles()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(
            {p["name"] for p in response.data}, {"test name", "second test"}
        )

    def test_add_answer(self):
        self.create_puzzle({"name": "test name", "url": TEST_URL})
        puzzle = Puzzle.objects.get()

        response = self.create_answer(puzzle.pk, {"text": "ans"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # This assumes no answer queue
        puzzle.refresh_from_db()
        self.assertEqual(puzzle.correct_answers(), ["ANS"])
        self.assertEqual(puzzle.status, Puzzle.SOLVED)

        response = self.create_answer(puzzle.pk, {"text": "ans"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.create_answer(puzzle.pk, {"text": ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.create_answer(puzzle.pk, {"text": "answer two"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        puzzle.refresh_from_db()
        self.assertEqual(puzzle.correct_answers(), ["ANS", "ANSWERTWO"])

    def test_delete_answer(self):
        self.create_puzzle({"name": "test name", "url": TEST_URL})
        puzzle = Puzzle.objects.get()

        self.create_answer(puzzle.pk, {"text": "ANSWER"})
        self.create_answer(puzzle.pk, {"text": "ANSWER TWO"})

        puzzle.refresh_from_db()
        self.assertEqual(puzzle.status, Puzzle.SOLVED)
        self.assertEqual(len(puzzle.correct_answers()), 2)
        guesses = list(puzzle.guesses.all())

        response = self.delete_answer(puzzle.pk, guesses[0].pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        puzzle.refresh_from_db()
        self.assertEqual(puzzle.status, Puzzle.SOLVED)
        self.assertEqual(len(puzzle.correct_answers()), 1)

        response = self.delete_answer(puzzle.pk, guesses[1].pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        puzzle.refresh_from_db()
        self.assertEqual(puzzle.status, Puzzle.SOLVING)
        self.assertEqual(len(puzzle.correct_answers()), 0)

    def test_edit_answer(self):
        self.create_puzzle({"name": "test name", "url": TEST_URL})
        puzzle = Puzzle.objects.get()

        self.create_answer(puzzle.pk, {"text": "ANSWER"})
        answer = puzzle.guesses.get()

        response = self.edit_answer(puzzle.pk, answer.pk, {"text": "oops real answer"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        answer.refresh_from_db()
        self.assertEqual(answer.text, "OOPSREALANSWER")

    def test_create_tag(self):
        self.create_puzzle({"name": "test name", "url": TEST_URL})
        puzzle = Puzzle.objects.get()

        response = self.create_tag(
            puzzle.pk, {"name": "taggy", "color": PuzzleTag.BLUE}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(puzzle.tags.count(), 1)
        # Should return a puzzle
        self.assertEqual(response.data["name"], puzzle.name)

    def test_delete_tag(self):
        self.create_puzzle({"name": "test name", "url": TEST_URL})
        puzzle = Puzzle.objects.get()
        self.create_tag(puzzle.pk, {"name": "taggy", "color": PuzzleTag.BLUE})
        self.assertEqual(puzzle.tags.count(), 1)
        tag = puzzle.tags.get()

        response = self.delete_tag(puzzle.pk, tag.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(puzzle.tags.count(), 0)
