import os

from django.test import TestCase
from accounts.models import Puzzler
from hunts.models import Hunt
from puzzles.models import Puzzle
from .models import Answer

class TestAnswers(TestCase):

    def setUp(self):
        self._user = Puzzler.objects.create_user(
            username='test', email='test@ing.com', password='testingpwd')
        self.client.login(username='test', password='testingpwd')

        self._test_hunt = Hunt.objects.create(name="fake hunt", url="google.com")

        self._puzzle = Puzzle.objects.create(
            name="test", hunt=self._test_hunt, url="fake_url.com",
            sheet="fakesheet.com", channel="0", is_meta=False)


    def tearDown(self):
        self._puzzle.delete()
        self._test_hunt.delete()
        self._user.delete()


    def test_answer_queue_page(self):
        response = self.client.get('/answers/queue/' + str(self._test_hunt.pk))
        self.assertEqual(response.status_code, 200)


    def test_answer_from_smallboard(self):
        self.assertEqual(list(self._puzzle.guesses.all()), [])
        self.assertEqual(self._puzzle.status, Puzzle.SOLVING)

        guess = 'a!@#1$%^&*() b  \t C \n d[2]{}\\\'"/?<>,. e~`'
        self.client.post("/puzzles/guess/{}/".format(self._puzzle.pk), {"text": guess})

        sanitized = 'A1BCD2E'
        self.assertEqual([a.text for a in self._puzzle.guesses.all()], [sanitized])
        self._puzzle.refresh_from_db()
        self.assertEqual(self._puzzle.status, Puzzle.PENDING)


    def test_answer_from_slack(self):
        self.assertEqual(list(self._puzzle.guesses.all()), [])
        self.assertEqual(self._puzzle.status, Puzzle.SOLVING)

        self.client.post("/puzzles/slack_guess/", {"channel_id": "0", "text": "guess"})

        self.assertEqual([a.text for a in self._puzzle.guesses.all()], ["GUESS"])
        self._puzzle.refresh_from_db()
        self.assertEqual(self._puzzle.status, Puzzle.PENDING)


    def test_answer_queue_status(self):
        guess = Answer.objects.create(puzzle=self._puzzle, text="guess")
        self.assertEqual(guess.status, Answer.NEW)

        self.client.post("/answers/queue/{}/{}".format(self._test_hunt.pk, guess.pk),
            {"status": Answer.SUBMITTED})
        self._puzzle.refresh_from_db()
        self.assertEqual(self._puzzle.status, Puzzle.PENDING)

        self.client.post("/answers/queue/{}/{}".format(self._test_hunt.pk, guess.pk),
            {"status": Answer.PARTIAL})
        self._puzzle.refresh_from_db()
        self.assertEqual(self._puzzle.status, Puzzle.SOLVING)

        note = "test puzzle note"
        self.client.post("/answers/update_note/{}".format(guess.pk), {"text": note})
        guess.refresh_from_db()
        self.assertEqual(guess.response, note)

        self.client.post("/answers/queue/{}/{}".format(self._test_hunt.pk, guess.pk),
            {"status": Answer.INCORRECT})
        self._puzzle.refresh_from_db()
        self.assertEqual(self._puzzle.status, Puzzle.SOLVING)

        self.client.post("/answers/queue/{}/{}".format(self._test_hunt.pk, guess.pk),
            {"status": Answer.CORRECT})
        self._puzzle.refresh_from_db()
        self.assertEqual(self._puzzle.status, Puzzle.SOLVED)
        self.assertEqual(self._puzzle.answer, guess.text)

        self.client.post("/answers/queue/{}/{}".format(self._test_hunt.pk, guess.pk),
            {"status": Answer.INCORRECT})
        self._puzzle.refresh_from_db()
        self.assertEqual(self._puzzle.status, Puzzle.SOLVING)
        self.assertEqual(self._puzzle.answer, "")


    def test_deleting_puzzle(self):
        deleted_puzzle = Puzzle.objects.create(
            name="delete", hunt=self._test_hunt, url="delete.com",
            sheet="delete.com", channel="1", is_meta=False)
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
