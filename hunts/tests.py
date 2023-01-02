from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from accounts.models import Puzzler
from answers.models import Answer
from puzzles.models import Puzzle
from puzzles.puzzle_tag import PuzzleTag

from .chart_utils import *
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

        self.assertEqual(len(list(hunt.get_progression_puzzles())), 3)

    def test_meta_list(self):
        hunt = self.create_hunt("test_hunt")

        meta1 = self.create_puzzle("meta1", hunt, True)
        meta2 = self.create_puzzle("meta2", hunt, True)
        guess_meta1 = Answer.objects.create(text="meta1", puzzle=meta1)
        guess_meta1.set_status(Answer.CORRECT)
        guess_meta2 = Answer.objects.create(text="meta2", puzzle=meta2)
        guess_meta2.set_status(Answer.CORRECT)

        self.assertEqual(
            hunt.get_meta_solve_list(),
            [[meta2.name, meta2.solved_time()], [meta1.name, meta1.solved_time()]],
        )

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
        self.assertEqual(hunt_timed.get_minutes_per_solve(recent=True), mps_string)
        self.assertEqual(hunt_timed.get_solves_per_hour(recent=True), sph_string)

    def test_chart_utils_untimed(self):
        unsolved_name = "puzzle_unsolved"

        # test behavior for a hunt with no start time
        hunt_untimed = self.create_hunt("hunt_untimed")
        self.assertFalse(can_use_chart(hunt_untimed))
        self.assertIsNone(get_chart_data(hunt_untimed))

        puzzle_unsolved = self.create_puzzle(unsolved_name, hunt_untimed, False)
        self.assertTrue(can_use_chart(hunt_untimed))
        chart_data = get_chart_data(hunt_untimed)
        self.assertIsNotNone(chart_data)
        labels, times, counts, is_meta = chart_data
        self.assertEqual(times[0], puzzle_unsolved.created_on.isoformat())

    def test_chart_utils(self):
        meta_name = "puzzle_meta"
        solved_name = "puzzle_solved"
        unsolved_name = "puzzle_unsolved"
        start_pt_name = "Start"
        cur_pt_name = "Now"

        # test behavior for a future hunt
        hunt_future = self.create_hunt(
            "hunt_future", start=timezone.now() + timedelta(days=100)
        )
        self.assertFalse(can_use_chart(hunt_future))

        # test behavior for a current hunt w/ unsolved, solved, and meta puzzles
        hunt_current = self.create_hunt(
            "hunt_current",
            start=timezone.now(),
            end=timezone.now() + timedelta(days=100),
        )
        puzzle_unsolved = self.create_puzzle(unsolved_name, hunt_current, False)
        puzzle_solved = self.create_puzzle(solved_name, hunt_current, False)
        guess_solved = Answer.objects.create(text="guess", puzzle=puzzle_solved)
        guess_solved.set_status(Answer.CORRECT)
        self.assertEqual(puzzle_solved.status, Puzzle.SOLVED)
        puzzle_meta = self.create_puzzle(meta_name, hunt_current, True)
        guess_meta = Answer.objects.create(text="guess", puzzle=puzzle_meta)
        guess_meta.set_status(Answer.CORRECT)
        self.assertEqual(puzzle_meta.status, Puzzle.SOLVED)

        # test get_chart_data()
        labels, times, counts, is_meta = get_chart_data(hunt_current)
        self.assertEqual(labels, [start_pt_name, solved_name, meta_name, cur_pt_name])
        self.assertEqual(
            times[:3],
            [
                hunt_current.start_time.isoformat(),
                puzzle_solved.solved_time().isoformat(),
                puzzle_meta.solved_time().isoformat(),
            ],
        )
        self.assertEqual(counts, [0, 1, 2, 2])
        self.assertEqual(is_meta, [False, False, True, False])

        # test get_chart_data() with unlocks
        labels, times, counts = get_chart_data(hunt_current, unlocks=True)
        self.assertEqual(
            labels, [start_pt_name, unsolved_name, solved_name, meta_name, cur_pt_name]
        )
        self.assertEqual(
            times[:4],
            [
                hunt_current.start_time.isoformat(),
                puzzle_unsolved.created_on.isoformat(),
                puzzle_solved.created_on.isoformat(),
                puzzle_meta.created_on.isoformat(),
            ],
        )
        self.assertEqual(counts, [0, 1, 2, 3, 3])

    def test_chart_utils_past(self):
        # test behavior when hunt.end_time is in the past
        solved_name = "puzzle_solved"
        start_pt_name = "Start"
        end_pt_name = "End"

        hunt_past = self.create_hunt(
            "hunt_past",
            start=timezone.now() - timedelta(days=100),
            end=timezone.now() - timedelta(days=1),
        )
        solve_after_end = self.create_puzzle(solved_name, hunt_past, False)
        labels, times, counts, is_meta = get_chart_data(hunt_past)
        self.assertEqual(labels, [start_pt_name, end_pt_name])
        self.assertEqual(
            times, [hunt_past.start_time.isoformat(), hunt_past.end_time.isoformat()]
        )


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

    def test_default_tag_creation(self):
        PuzzleTag.create_default_tags(self._test_hunt)

        for (name, color) in PuzzleTag.DEFAULT_TAGS:
            self.assertTrue(
                PuzzleTag.objects.filter(
                    hunt=self._test_hunt, name=name, color=color
                ).exists()
            )

    def test_unused_default_tag_deletion(self):
        PuzzleTag.create_default_tags(self._test_hunt)
        PuzzleTag.remove_default_tags(self._test_hunt)

        for (name, color) in PuzzleTag.DEFAULT_TAGS:
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

        for (name, color) in PuzzleTag.DEFAULT_TAGS:
            self.assertTrue(
                PuzzleTag.objects.filter(
                    hunt=self._test_hunt, name=name, color=color
                ).exists()
            )
