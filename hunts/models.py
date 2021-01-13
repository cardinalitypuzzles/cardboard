from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.utils import timezone
from puzzles.models import Puzzle
from datetime import timedelta


class Hunt(models.Model):
    name = models.CharField(max_length=128)
    url = models.URLField()
    created_on = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(default=None, blank=True, null=True)
    end_time = models.DateTimeField(default=None, blank=True, null=True)

    puzzlers = models.ManyToManyField(get_user_model(), related_name="hunts")
    active = models.BooleanField(default=True)
    slug = models.SlugField(blank=True, unique=True)
    answer_queue_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @staticmethod
    def get_object_or_404(user=None, **kwargs):
        hunt = get_object_or_404(Hunt, **kwargs)
        if user and user.is_authenticated and user.last_accessed_hunt != hunt:
            user.last_accessed_hunt = hunt
            user.save(update_fields=["last_accessed_hunt"])
        return hunt

    def get_num_solved(self):
        return self.puzzles.filter(status=Puzzle.SOLVED).count()

    def get_num_unsolved(self):
        return self.puzzles.filter(~Q(status=Puzzle.SOLVED)).count()

    def get_num_unlocked(self):
        return self.puzzles.count()

    def get_num_metas_solved(self):
        return self.puzzles.filter(Q(status=Puzzle.SOLVED), Q(is_meta=True)).count()

    def get_num_metas_unsolved(self):
        return self.puzzles.filter(~Q(status=Puzzle.SOLVED), Q(is_meta=True)).count()

    # Gets the number of puzzles that are either solved or feed into a solved meta.
    def get_progression(self):
        # the second WITH is a workaround psql error: recursive reference in a subquery
        query = """
        WITH RECURSIVE progression_puzzles (id) AS (
            SELECT id
            FROM puzzles_puzzle
            WHERE (status = 'SOLVED' AND hunt_id = %s)
            UNION
            SELECT * FROM (
                WITH progression_ids AS (
                    SELECT id FROM progression_puzzles
                )
                SELECT Metas.from_puzzle_id
                FROM puzzles_puzzle_metas Metas
                WHERE Metas.to_puzzle_id IN (SELECT * FROM progression_ids)
            ) AS progression_update
        )
        SELECT id FROM progression_puzzles
        """
        progression_ids = Hunt.objects.raw(query, [str(self.pk)])
        return len(list(progression_ids))

    # Returns a list of solved meta names and solve times in [name, time] pairs.
    # Solve times are given in dd hh:mm (am/pm) format (e.g., Fr 4:00 pm).
    def get_meta_solve_list(self):
        solved_metas = self.puzzles.filter(Q(status=Puzzle.SOLVED), Q(is_meta=True))
        sorted_solved_metas = sorted(solved_metas, key=lambda x: x.solved_time())

        return [[p.name, p.solved_time()] for p in sorted_solved_metas]

    # Returns ends of the time interval for the time stats (6 hrs or entire hunt)
    # and # of solves within the interval.
    def time_stats_helper(self, recent=False):
        interval_end = timezone.now()
        if self.end_time:
            interval_end = min(interval_end, self.end_time)
        if not self.start_time or self.start_time >= interval_end:
            return None

        interval_start = self.start_time
        if recent:
            interval_start = max(interval_start, interval_end - timedelta(hours=6))

        solved = self.get_num_solved()
        if recent:
            solved_puzzles = self.puzzles.filter(Q(status=Puzzle.SOLVED))
            solved = len(
                [x for x in solved_puzzles if x.solved_time() >= interval_start]
            )

        return solved, interval_start, interval_end

    def get_solves_per_hour(self, recent=False):
        time_stats_info = self.time_stats_helper(recent=recent)
        if not time_stats_info:
            return "N/A"
        solved, interval_start, interval_end = time_stats_info

        hours_elapsed = (interval_end - interval_start).total_seconds() / 3600
        return "{:.2f}".format(round(solved / hours_elapsed, 2))

    def get_minutes_per_solve(self, recent=False):
        time_stats_info = self.time_stats_helper(recent=recent)
        if not time_stats_info:
            return "N/A"
        solved, interval_start, interval_end = time_stats_info

        if solved == 0:
            return "N/A"

        minutes_elapsed = (interval_end - interval_start).total_seconds() / 60
        return "{:.2f}".format(round(minutes_elapsed / solved, 2))
