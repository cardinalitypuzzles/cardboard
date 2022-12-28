import json
from django.test import override_settings
from unittest.mock import patch
from rest_framework.test import APITestCase

from accounts.models import Puzzler
from chat.models import ChatRoom
from chat.fake_service import FakeChatService
from hunts.models import Hunt
from answers.models import Answer
from .models import Puzzle, is_ancestor
from .puzzle_tag import PuzzleTag


@override_settings(
    CHAT_DEFAULT_SERVICE="FAKE",
    CHAT_SERVICES={
        "FAKE": FakeChatService,
    },
)
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

    def test_empty_custom_tags_deletion(self):
        # test that a empty custom tag is reaped
        puzzle = self.create_puzzle("puzzle", False)
        custom_tag = PuzzleTag.objects.create(
            name="custom", hunt=self._test_hunt, is_default=False
        )
        puzzle.tags.add(custom_tag)
        self.client.delete(
            f"/api/v1/puzzles/{puzzle.pk}/tags/{custom_tag.pk}",
        )
        self.assertFalse(
            PuzzleTag.objects.filter(hunt=self._test_hunt, name="custom").exists()
        )

    def test_empty_default_tags_deletion(self):
        # test that a empty default tag is NOT reaped
        puzzle = self.create_puzzle("puzzle", False)
        PuzzleTag.create_default_tags(self._test_hunt)

        for tag in PuzzleTag.objects.filter(is_default=True):
            puzzle.tags.add(tag)

            self.client.delete(
                f"/api/v1/puzzles/{puzzle.pk}/tags/{tag.pk}",
            )

        for (name, color) in PuzzleTag.DEFAULT_TAGS:
            self.assertTrue(
                PuzzleTag.objects.filter(
                    hunt=self._test_hunt, name=name, color=color
                ).exists()
            )

    def test_sheets_redirect(self):
        puzzle = self.create_puzzle("test_redirects", False)
        response = self.client.get(f"/puzzles/s/{puzzle.pk}", follow=False)
        self.assertEqual(response["Location"], puzzle.sheet)

        response = self.client.get(f"/puzzles/s/0", follow=False)
        self.assertEqual(response["Location"], "/")

        Puzzle.objects.select_for_update().filter(id=puzzle.pk).update(sheet=None)
        response = self.client.get(f"/puzzles/s/{puzzle.pk}", follow=False)
        self.assertEqual(response["Location"], "/")

    def test_create_embedded_urls(self):
        puzzle = self.create_puzzle("test_redirects", False)
        field_url_map = puzzle.create_field_url_map()
        self.assertEqual(field_url_map["Puzzle"], puzzle.url)
        self.assertEqual(field_url_map["Sheet"], puzzle.sheet)
        self.assertNotIn("Text Channel", field_url_map)
        self.assertNotIn("Voice Channel", field_url_map)

        puzzle.chat_room = ChatRoom.objects.create(name="test_room")
        puzzle.chat_room.audio_channel_url = "audio_channel_url.com"
        puzzle.chat_room.text_channel_url = "text_channel_url.com"
        field_url_map = puzzle.create_field_url_map()
        self.assertEqual(field_url_map["Puzzle"], puzzle.url)
        self.assertEqual(field_url_map["Sheet"], puzzle.sheet)
        self.assertEqual(field_url_map["Text Channel"], "text_channel_url.com")
        self.assertEqual(field_url_map["Voice Channel"], "audio_channel_url.com")

    def test_is_backsolved(self):
        feeder = self.create_puzzle("feeder", False)
        self.assertFalse(feeder.is_backsolved())

        self.client.post(
            f"/api/v1/puzzles/{feeder.pk}/tags",
            {"name": PuzzleTag.BACKSOLVED.upper(), "color": "primary"},
        )
        # Not backsolved as it hasn't been solved yet
        self.assertFalse(feeder.is_backsolved())

        guess = Answer.objects.create(text="guess", puzzle=feeder)
        guess.set_status(Answer.CORRECT)
        # Now we're backsolved!
        self.assertTrue(feeder.is_backsolved())

        tag = feeder.tags.get(name=PuzzleTag.BACKSOLVED.upper())
        self.client.delete(f"/api/v1/puzzles/{feeder.pk}/tags/{tag.id}")
        # Missing the tag
        self.assertFalse(feeder.is_backsolved())

        # Lowercase tag should work too
        self.client.post(
            f"/api/v1/puzzles/{feeder.pk}/tags",
            {"name": PuzzleTag.BACKSOLVED.lower(), "color": "primary"},
        )
        # Now it should be backsolved again
        self.assertTrue(feeder.is_backsolved())
