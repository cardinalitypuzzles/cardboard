from django.test import TestCase
from guardian.shortcuts import assign_perm

from accounts.models import Puzzler
from hunts.models import Hunt
from puzzles.models import Puzzle

from .models import Answer


class TestAnswers(TestCase):
    def setUp(self):
        self._user = Puzzler.objects.create_user(
            username="test", email="test@ing.com", password="testingpwd"
        )
        self.client.login(username="test", password="testingpwd")

        self._test_hunt = Hunt.objects.create(name="fake hunt", url="google.com")
        assign_perm("hunt_admin", self._user, self._test_hunt)
        assign_perm("hunt_access", self._user, self._test_hunt)

        self._puzzle = Puzzle.objects.create(
            name="test",
            hunt=self._test_hunt,
            url="fake_url.com",
            sheet="fakesheet.com",
            is_meta=False,
        )

    def tearDown(self):
        self._puzzle.delete()
        self._test_hunt.delete()
        self._user.delete()

    def test_answer_queue_page(self):
        response = self.client.get("/answers/queue/" + str(self._test_hunt.slug))
        self.assertEqual(response.status_code, 200)

    def test_answer_from_cardboard(self):
        self.assertEqual(list(self._puzzle.guesses.all()), [])
        self.assertEqual(self._puzzle.status, Puzzle.SOLVING)

        guess = "a!@#1$%^&*() b  \t C \n d[2]{}\\'\"/?<>,. e~`"
        self.client.post(
            "/api/v1/puzzles/{}/answers".format(self._puzzle.pk),
            {"text": guess},
        )

        sanitized = "A!@#1$%^&*()BCD[2]{}\\'\"/?<>,.E~`"
        self.assertEqual([a.text for a in self._puzzle.guesses.all()], [sanitized])
        self._puzzle.refresh_from_db()
        # By default, answer_queue_enabled is false. In such a case, submitting
        # an answer will change the status to SOLVED.
        self.assertEqual(self._puzzle.status, Puzzle.SOLVED)

    def test_answer_queue_status(self):
        guess = Answer.objects.create(puzzle=self._puzzle, text="guess")
        self.assertEqual(guess.status, Answer.NEW)

        self.client.post(
            "/answers/queue/{}/{}".format(self._test_hunt.slug, guess.pk),
            {"status": Answer.SUBMITTED},
        )
        self._puzzle.refresh_from_db()
        self.assertEqual(self._puzzle.status, Puzzle.PENDING)

        self.client.post(
            "/answers/queue/{}/{}".format(self._test_hunt.slug, guess.pk),
            {"status": Answer.PARTIAL},
        )
        self._puzzle.refresh_from_db()
        self.assertEqual(self._puzzle.status, Puzzle.SOLVING)

        note = "test puzzle note"
        self.client.post("/answers/update_note/{}".format(guess.pk), {"text": note})
        guess.refresh_from_db()
        self.assertEqual(guess.response, note)

        self.client.post(
            "/answers/queue/{}/{}".format(self._test_hunt.slug, guess.pk),
            {"status": Answer.INCORRECT},
        )
        self._puzzle.refresh_from_db()
        self.assertEqual(self._puzzle.status, Puzzle.SOLVING)

        self.client.post(
            "/answers/queue/{}/{}".format(self._test_hunt.slug, guess.pk),
            {"status": Answer.CORRECT},
        )
        self._puzzle.refresh_from_db()
        self.assertEqual(self._puzzle.status, Puzzle.SOLVED)
        self.assertEqual(self._puzzle.answer, guess.text)

        self.client.post(
            "/answers/queue/{}/{}".format(self._test_hunt.slug, guess.pk),
            {"status": Answer.INCORRECT},
        )
        self._puzzle.refresh_from_db()
        self.assertEqual(self._puzzle.status, Puzzle.SOLVING)
        self.assertEqual(self._puzzle.answer, "")

    def test_deleting_puzzle(self):
        deleted_puzzle = Puzzle.objects.create(
            name="delete",
            hunt=self._test_hunt,
            url="delete.com",
            sheet="delete.com",
            is_meta=False,
        )
        guess = Answer.objects.create(puzzle=deleted_puzzle, text="guess")
        self.assertEqual(Answer.objects.filter(pk=guess.pk).exists(), True)
        deleted_puzzle.delete()
        self.assertEqual(Answer.objects.filter(pk=guess.pk).exists(), False)

    def test_multiple_answers(self):
        guess1 = Answer.objects.create(puzzle=self._puzzle, text="guess1")
        guess2 = Answer.objects.create(puzzle=self._puzzle, text="guess2")

        guess1.set_status(Answer.CORRECT)
        self._puzzle.refresh_from_db()
        self.assertEqual(self._puzzle.status, Puzzle.SOLVED)
        self.assertEqual(self._puzzle.answer, guess1.text)

        # this should not affect puzzle status if it is already solved
        guess2.set_status(Answer.INCORRECT)
        self._puzzle.refresh_from_db()
        self.assertEqual(self._puzzle.status, Puzzle.SOLVED)
        self.assertEqual(self._puzzle.answer, guess1.text)
