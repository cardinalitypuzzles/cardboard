from django.test import TestCase

from accounts.models import Puzzler
from .models import Hunt
from puzzles.models import Puzzle
from answers.models import Answer


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

    def test_stats(self):
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

        self.assertEqual(hunt.get_num_solved(), 2)
        self.assertEqual(hunt.get_num_unsolved(), 3)
        self.assertEqual(hunt.get_num_unlocked(), 5)
        self.assertEqual(hunt.get_num_metas_solved(), 1)
