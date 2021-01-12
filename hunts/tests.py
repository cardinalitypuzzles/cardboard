from django.test import TestCase
from django.utils import timezone

from accounts.models import Puzzler
from .models import Hunt
from .forms import HuntForm
from puzzles.models import Puzzle
from answers.models import Answer

from datetime import timedelta


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

    def test_stats(self):
        hunt = self.create_hunt("test_hunt")

        puzzle1 = self.create_puzzle("solved", hunt, False)
        puzzle2 = self.create_puzzle("unsolved_a", hunt, False)
        puzzle3 = self.create_puzzle("unsolved_b", hunt, False)
        meta = self.create_puzzle("meta", hunt, True)
        feeder = self.create_puzzle("feeder", hunt, False)
        feeder.metas.add(meta)
        self.assertEqual(hunt.get_num_metas_unsolved(), 1)

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
        self.assertEqual(hunt.get_num_metas_unsolved(), 0)

        self.assertEqual(hunt.get_progression(), 3)

    def test_time_stats(self):
        hunt_untimed = self.create_hunt("hunt_untimed")
        self.assertEqual(hunt_untimed.get_minutes_per_solve(), "N/A")
        self.assertEqual(hunt_untimed.get_solves_per_hour(), "N/A")

        start_time = timezone.now() - timedelta(hours=1)
        end_time = start_time + timedelta(days=100)
        hunt_timed = self.create_hunt("hunt_timed", start=start_time, end=end_time)
        self.assertEqual(hunt_timed.get_minutes_per_solve(), "N/A")
        self.assertEqual(hunt_timed.get_solves_per_hour(), "0.00")

        puzzle = self.create_puzzle("test_puzzle", hunt_timed, False)
        guess = Answer.objects.create(text="guess", puzzle=puzzle)
        guess.set_status(Answer.CORRECT)

        solve_time = puzzle.solved_time() - hunt_timed.start_time
        minutes_elapsed = solve_time.total_seconds() / 60
        mps_string = "{:.2f}".format(round(minutes_elapsed, 2))
        sph_string = "{:.2f}".format(round(1 / (minutes_elapsed / 60), 2))
        self.assertEqual(hunt_timed.get_minutes_per_solve(), mps_string)
        self.assertEqual(hunt_timed.get_solves_per_hour(), sph_string)


class HuntFormTests(TestCase):
    def setUp(self):
        self._user = Puzzler.objects.create_user(
            username="test", email="test@ing.com", password="testingpwd"
        )
        self.client.login(username="test", password="testingpwd")

    def tearDown(self):
        self._user.delete()

    def test_times_missing_start(self):
        # Start and end time inputs come from the SplitDateTimeWidget
        data = {
            "name": "test",
            "url": "example.com",
            "end_time_0": "2020-01-01",
            "end_time_1": "12:00",
        }

        form = HuntForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.non_field_errors(), ["Start time must be provided with end time."]
        )

    def test_times_end_before_start(self):
        # Start and end time inputs come from the SplitDateTimeWidget
        data = {
            "name": "test",
            "url": "example.com",
            "start_time_0": "2020-02-02",
            "start_time_1": "12:00",
            "end_time_0": "2020-01-01",
            "end_time_1": "12:00",
        }

        form = HuntForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.non_field_errors(), ["End time must be after start time."]
        )
