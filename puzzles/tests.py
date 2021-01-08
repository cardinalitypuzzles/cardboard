import json
from unittest.mock import patch

from rest_framework.test import APITestCase

from accounts.models import Puzzler
from hunts.models import Hunt
from answers.models import Answer
from .models import Puzzle, is_ancestor
from .puzzle_tree import PuzzleTree
from .puzzle_tag import PuzzleTag


class TestPuzzle(APITestCase):
    def setUp(self):
        self._user = Puzzler.objects.create_user(
            username="test", email="test@ing.com", password="testingpwd"
        )
        self.client.login(username="test", password="testingpwd")

        self._test_hunt = Hunt.objects.create(name="fake hunt", url="google.com")
        self._suffix = 0
        self._puzzles = []

    def tearDown(self):
        for p in self._puzzles:
            p.delete()

        for tag in PuzzleTag.objects.all():
            tag.delete()

        self._test_hunt.delete()

    def create_puzzle(self, name, is_meta=False):
        fake_url = "fakeurl%i.com" % self._suffix
        fake_sheet = "fakesheet%i.com" % self._suffix
        self._suffix += 1

        puzzle = Puzzle.objects.create(
            name=name,
            hunt=self._test_hunt,
            url=fake_url,
            sheet=fake_sheet,
            is_meta=is_meta,
        )
        self._puzzles.append(puzzle)
        return puzzle

    def test_solved_time(self):
        test_puzzle = self.create_puzzle("test_puzzle", False)
        self.assertFalse(test_puzzle.is_solved())
        self.assertEqual(test_puzzle.solved_time(), None)

        guess1 = Answer.objects.create(text="guess1", puzzle=test_puzzle)
        guess1.set_status(Answer.CORRECT)
        self.assertTrue(test_puzzle.is_solved())
        self.assertEqual(test_puzzle.solved_time(), guess1.created_on)

        guess2 = Answer.objects.create(text="guess2", puzzle=test_puzzle)
        guess2.set_status(Answer.CORRECT)
        self.assertEqual(test_puzzle.solved_time(), guess2.created_on)

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

        np_pairs = PuzzleTree(
            [puzzle1_1, puzzle1_2, meta1, puzzle_dangling]
        ).get_sorted_node_parent_pairs()

        expected = [
            "node: unit_puzzle_dangling parent: None",
            "node: unit_meta1 parent: None",
            "node: unit_puzzle1-2 parent: unit_meta1",
            "node: unit_puzzle1-1 parent: unit_meta1",
        ]
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

        np_pairs = PuzzleTree(
            [puzzle1, puzzle2, meta1, meta2]
        ).get_sorted_node_parent_pairs()

        expected = [
            "node: unit_meta1 parent: None",
            "node: unit_puzzle2 parent: unit_meta1",
            "node: unit_puzzle1 parent: unit_meta1",
            "node: unit_puzzle2 parent: unit_puzzle1",
            "node: unit_meta2 parent: None",
            "node: unit_puzzle2 parent: unit_meta2",
            "node: unit_puzzle1 parent: unit_meta2",
            "node: unit_puzzle2 parent: unit_puzzle1",
        ]
        self.assertEqual([pair.__str__() for pair in np_pairs], expected)

    def test_meta_creates_tag(self):
        meta = self.create_puzzle("meta", True)
        self.assertTrue(
            PuzzleTag.objects.filter(name=meta.name, hunt=meta.hunt).exists()
        )
        self.assertTrue(meta.tags.filter(name=meta.name).exists())
        tag = meta.tags.get(name=meta.name)
        self.assertTrue(tag.is_meta)

    def test_meta_affects_tags(self):
        meta = self.create_puzzle("meta", True)
        feeder = self.create_puzzle("feeder", False)

        self.assertFalse(feeder.tags.filter(name=meta.name).exists())
        feeder.metas.add(meta)
        self.assertTrue(feeder.tags.filter(name=meta.name).exists())

    def test_tag_affects_meta(self):
        meta = self.create_puzzle("meta", True)
        feeder = self.create_puzzle("feeder", False)

        self.client.post(
            f"/api/v1/puzzles/{feeder.pk}/tags",
            {"name": meta.name, "color": "primary"},
        )
        self.assertTrue(feeder.metas.filter(pk=meta.pk).exists())

        tag = feeder.tags.get(name=meta.name)
        self.client.delete(f"/api/v1/puzzles/{feeder.pk}/tags/{tag.id}")
        self.assertFalse(feeder.metas.filter(pk=meta.pk).exists())

    def test_meta_created_after_tag(self):
        feeder = self.create_puzzle("feeder", False)
        tag = PuzzleTag.objects.create(name="Unknown Meta", hunt=feeder.hunt)
        feeder.tags.add(tag)
        self.assertFalse(
            PuzzleTag.objects.get(name="Unknown Meta", hunt=feeder.hunt).is_meta
        )

        meta = self.create_puzzle("Unknown Meta", True)
        self.assertTrue(
            PuzzleTag.objects.get(name="Unknown Meta", hunt=feeder.hunt).is_meta
        )
        self.assertTrue(feeder.metas.filter(pk=meta.pk).exists())

    def test_meta_puzzle_changes_affect_tags(self):
        meta = self.create_puzzle("oldname", True)
        feeder = self.create_puzzle("feeder", False)
        feeder.metas.add(meta)
        self.assertTrue(feeder.tags.filter(name="oldname").exists())

        self.client.patch(
            f"/api/v1/hunts/{self._test_hunt.pk}/puzzles/{meta.pk}",
            {"name": "newname"},
        )
        self.assertFalse(
            PuzzleTag.objects.filter(name="oldname", hunt=meta.hunt).exists()
        )
        self.assertTrue(feeder.tags.filter(name="newname").exists())
