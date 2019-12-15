from django.test import TestCase

from hunts.models import *
from .models import *
from .puzzle_tree import *

class TestPuzzleTree(TestCase):
    def setUp(self):
        self._test_hunt = Hunt.objects.create(name="fake hunt", url="google.com")
        self._suffix = 0
        self._puzzles = []

    def tearDown(self):
        for p in self._puzzles:
            p.delete()
        self._test_hunt.delete()

    def create_puzzle(self, name, is_meta=False):
        fake_url = "fakeurl%i.com" % self._suffix
        fake_sheet = "fakesheet%i.com" % self._suffix
        fake_channel = str(self._suffix)
        self._suffix += 1

        puzzle = Puzzle.objects.create(name=name, hunt=self._test_hunt, url=fake_url,
                                       sheet=fake_sheet, channel=fake_channel)
        self._puzzles.append(puzzle)
        return puzzle


    #def test_empty(self):
    #    self.assertEqual(PuzzleTree([]).getSortedPuzzles(), [])

    def test_basic(self):
        meta1 = self.create_puzzle("meta1", True)
        puzzle1_1 = self.create_puzzle("puzzle1-1")
        puzzle1_2 = self.create_puzzle("puzzle1-2")

        puzzle1_1.metas.add(meta1)
        puzzle1_2.metas.add(meta1)

        puzzle1_1.status = Puzzle.SOLVED

        puzzle_dangling = self.create_puzzle("puzzle_dangling")

        sorted_nodes = PuzzleTree([puzzle1_1, puzzle1_2, meta1, puzzle_dangling]).getSortedPuzzles()
        expected = ["puzzle_dangling", "meta1", "puzzle1-2", "puzzle1-1"]
        self.assertEqual([node.puzzle.__str__() for node in sorted_nodes], expected)
