from django.test import TestCase

from hunts.models import *
from .models import *
from .puzzle_tree import *

class TestPuzzle(TestCase):
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

    def test_is_ancestor(self):
        meta1 = self.create_puzzle("unit_meta1", True)
        meta2 = self.create_puzzle("unit_meta2", True)
        meta3 = self.create_puzzle("unit_meta3", True)

        self.assertTrue(is_ancestor(meta1, meta1))
        self.assertFalse(is_ancestor(meta1, meta2))

        meta1.metas.add(meta2)
        meta2.metas.add(meta3)
        self.assertFalse(is_ancestor(meta1, meta2))
        self.assertTrue(is_ancestor(meta2, meta1))
        self.assertFalse(is_ancestor(meta2, meta3))
        self.assertTrue(is_ancestor(meta3, meta2))
        self.assertFalse(is_ancestor(meta1, meta3))
        self.assertTrue(is_ancestor(meta3, meta1))

    def test_empty_tree(self):
        self.assertEqual(PuzzleTree([]).get_sorted_node_parent_pairs(), [])

    def test_basic_tree(self):
        meta1 = self.create_puzzle("unit_meta1", True)
        puzzle1_1 = self.create_puzzle("unit_puzzle1-1")
        puzzle1_2 = self.create_puzzle("unit_puzzle1-2")

        puzzle1_1.metas.add(meta1)
        puzzle1_2.metas.add(meta1)

        puzzle1_1.status = Puzzle.SOLVED

        puzzle_dangling = self.create_puzzle("unit_puzzle_dangling")

        np_pairs = PuzzleTree([puzzle1_1, puzzle1_2, meta1, puzzle_dangling]).get_sorted_node_parent_pairs()

        expected = ["node: unit_puzzle_dangling parent: None",
                    "node: unit_meta1 parent: None",
                    "node: unit_puzzle1-2 parent: unit_meta1",
                    "node: unit_puzzle1-1 parent: unit_meta1"]
        self.assertEqual([pair.__str__() for pair in np_pairs], expected)

    def test_overlapping_metas_tree(self):
        meta1 = self.create_puzzle("unit_meta1", True)
        meta2 = self.create_puzzle("unit_meta2", True)
        puzzle1 = self.create_puzzle("unit_puzzle1", True)
        puzzle2 = self.create_puzzle("unit_puzzle2")

        puzzle1.metas.add(meta1)
        puzzle1.metas.add(meta2)
        puzzle2.metas.add(meta1)
        puzzle2.metas.add(meta2)
        puzzle2.metas.add(puzzle1)

        np_pairs = PuzzleTree([puzzle1, puzzle2, meta1, meta2]).get_sorted_node_parent_pairs()

        expected = ["node: unit_meta1 parent: None",
                    "node: unit_puzzle2 parent: unit_meta1",
                    "node: unit_puzzle1 parent: unit_meta1",
                    "node: unit_puzzle2 parent: unit_puzzle1",
                    "node: unit_meta2 parent: None",
                    "node: unit_puzzle2 parent: unit_meta2",
                    "node: unit_puzzle1 parent: unit_meta2",
                    "node: unit_puzzle2 parent: unit_puzzle1"]
        self.assertEqual([pair.__str__() for pair in np_pairs], expected)
