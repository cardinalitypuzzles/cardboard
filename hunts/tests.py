from django.test import TestCase

from accounts.models import Puzzler
from answers.models import Answer
from puzzles.models import Puzzle
from puzzles.puzzle_tag import PuzzleTag

from .forms import HuntForm
from .models import Hunt


class TestHunt(TestCase):
    def setUp(self):
        self._user = Puzzler.objects.create_user(
            username="test", email="test@ing.com", password="testingpwd"
        )
        self.client.login(username="test", password="testingpwd")

        self._suffix = 0
        self._hunts = []
        self._puzzles = {}

    def tearDown(self):
        for h in self._hunts:
            for p in self._puzzles[h.name]:
                p.delete()
            h.delete()

    def create_hunt(self, name, start=None, end=None):
        fake_url = "fakeurl%i.com" % self._suffix
        self._suffix += 1

        hunt = Hunt.objects.create(
            name=name,
            url=fake_url,
            start_time=start,
            end_time=end,
        )
        self._hunts.append(hunt)
        self._puzzles[name] = []
        return hunt

    def create_puzzle(self, name, hunt, is_meta=False):
        fake_url = "fakeurl%i.com" % self._suffix
        fake_sheet = "fakesheet%i.com" % self._suffix
        self._suffix += 1

        puzzle = Puzzle.objects.create(
            name=name,
            hunt=hunt,
            url=fake_url,
            sheet=fake_sheet,
            is_meta=is_meta,
        )
        self._puzzles[hunt.name].append(puzzle)
        return puzzle

    def test_progression_puzzles(self):
        hunt = self.create_hunt("test_hunt")

        puzzle1 = self.create_puzzle("solved", hunt, False)
        puzzle2 = self.create_puzzle("unsolved_a", hunt, False)
        puzzle3 = self.create_puzzle("unsolved_b", hunt, False)
        meta = self.create_puzzle("meta", hunt, True)
        feeder = self.create_puzzle("feeder", hunt, False)
        feeder.metas.add(meta)

        guess_puzzle1 = Answer.objects.create(text="guess1", puzzle=puzzle1)
        guess_puzzle1.set_status(Answer.CORRECT)
        guess_meta = Answer.objects.create(text="meta", puzzle=meta)
        guess_meta.set_status(Answer.CORRECT)

        self.assertTrue(puzzle1.is_solved())
        self.assertFalse(puzzle2.is_solved())
        self.assertFalse(puzzle3.is_solved())
        self.assertTrue(meta.is_solved())
        self.assertFalse(feeder.is_solved())

        self.assertEqual(len(list(hunt.get_progression_puzzles())), 3)


class HuntFormTests(TestCase):
    def setUp(self):
        self._user = Puzzler.objects.create_user(
            username="test", email="test@ing.com", password="testingpwd"
        )
        self._test_hunt = Hunt.objects.create(name="fake hunt", url="google.com")
        self.client.login(username="test", password="testingpwd")

    def tearDown(self):
        self._user.delete()

    def test_times_missing_start(self):
        data = {
            "name": "test",
            "url": "example.com",
            "end_time": "2020-01-01T12:00",
        }

        form = HuntForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.non_field_errors(), ["Start time must be provided with end time."]
        )

    def test_times_end_before_start(self):
        data = {
            "name": "test",
            "url": "example.com",
            "start_time": "2020-02-02T12:00",
            "end_time": "2020-01-01T12:00",
        }

        form = HuntForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.non_field_errors(), ["End time must be after start time."]
        )

    def test_default_tag_creation(self):
        PuzzleTag.create_default_tags(self._test_hunt)

        for name, color in PuzzleTag.DEFAULT_TAGS:
            self.assertTrue(
                PuzzleTag.objects.filter(
                    hunt=self._test_hunt, name=name, color=color
                ).exists()
            )

    def test_unused_default_tag_deletion(self):
        PuzzleTag.create_default_tags(self._test_hunt)
        PuzzleTag.remove_default_tags(self._test_hunt)

        for name, color in PuzzleTag.DEFAULT_TAGS:
            self.assertFalse(
                PuzzleTag.objects.filter(
                    hunt=self._test_hunt, name=name, color=color
                ).exists()
            )

    def test_used_default_tag_deletion(self):
        PuzzleTag.create_default_tags(self._test_hunt)
        puzzle = Puzzle.objects.create(
            name="puzzle",
            hunt=self._test_hunt,
            url="test.com",
            sheet="sheet.com",
            is_meta=False,
        )

        for tag in PuzzleTag.objects.filter(is_default=True):
            puzzle.tags.add(tag)

        PuzzleTag.remove_default_tags(self._test_hunt)

        for name, color in PuzzleTag.DEFAULT_TAGS:
            self.assertTrue(
                PuzzleTag.objects.filter(
                    hunt=self._test_hunt, name=name, color=color
                ).exists()
            )
