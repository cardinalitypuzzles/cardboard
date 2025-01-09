from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Case, Max, Q, When
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.utils import timezone
from guardian.shortcuts import get_users_with_perms

from puzzles.models import Puzzle, PuzzleTag


class Hunt(models.Model):
    name = models.CharField(max_length=128)
    url = models.URLField()
    created_on = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(default=None, blank=True, null=True)
    end_time = models.DateTimeField(default=None, blank=True, null=True)
    last_active_users_update_time = models.DateTimeField(
        default=None, blank=True, null=True
    )

    puzzlers = models.ManyToManyField(
        get_user_model(), related_name="hunts", blank=True
    )
    active = models.BooleanField(default=True)
    slug = models.SlugField(blank=True, unique=True)

    class Meta:
        permissions = (
            ("hunt_admin", "Hunt admin"),
            ("hunt_access", "Hunt access"),
        )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        if not hasattr(self, "settings"):
            HuntSettings.objects.create(hunt=self)

    @staticmethod
    def get_object_or_404(user=None, **kwargs):
        hunt = get_object_or_404(Hunt, **kwargs)
        if user and user.is_authenticated and user.last_accessed_hunt != hunt:
            user.last_accessed_hunt = hunt
            user.save(update_fields=["last_accessed_hunt"])
        return hunt

    def get_num_solved(self):
        return self.puzzles.filter(status=Puzzle.SOLVED).count()

    def get_num_backsolved(self):
        return self.puzzles.filter(
            status=Puzzle.SOLVED, tags__name=PuzzleTag.BACKSOLVED
        ).count()

    def get_num_freebie(self):
        return self.puzzles.filter(
            status=Puzzle.SOLVED, tags__name=PuzzleTag.FREEBIE
        ).count()

    def get_num_unsolved(self):
        return self.puzzles.filter(~Q(status=Puzzle.SOLVED)).count()

    def get_num_unlocked(self):
        return self.puzzles.count()

    def get_num_metas_solved(self):
        return self.puzzles.filter(Q(status=Puzzle.SOLVED), Q(is_meta=True)).count()

    def get_num_metas_unsolved(self):
        return self.puzzles.filter(~Q(status=Puzzle.SOLVED), Q(is_meta=True)).count()

    # Gets a RawQuerySet of puzzles that are either solved or only feed into solved metas.
    def get_progression_puzzles(self):
        query = """
        WITH RECURSIVE progression_puzzles (id) AS (
            SELECT id
            FROM puzzles_puzzle
            WHERE (status = 'SOLVED' AND hunt_id = %s)
            UNION
            SELECT Metas.from_puzzle_id
            FROM puzzles_puzzle_metas Metas
            INNER JOIN progression_puzzles ON progression_puzzles.id = Metas.to_puzzle_id
        )
        SELECT * FROM puzzles_puzzle WHERE id IN (SELECT id FROM progression_puzzles)
        """
        return Hunt.objects.raw(query, [str(self.pk)])

    # Returns a list of solved meta names and solve times in [name, time] pairs.
    # Pairs sorted by latest solves first.
    def get_meta_solve_list(self):
        solved_metas = (
            self.puzzles.filter(Q(status=Puzzle.SOLVED), Q(is_meta=True))
            .annotate(
                _solved_time=Max(
                    Case(When(guesses__status="CORRECT", then="guesses__created_on"))
                )
            )
            .order_by("-_solved_time")
        )

        return [[p.name, p._solved_time] for p in solved_metas]

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

        if recent:
            solved = (
                self.puzzles.filter(Q(status=Puzzle.SOLVED))
                .annotate(
                    _solved_time=Max(
                        Case(
                            When(guesses__status="CORRECT", then="guesses__created_on")
                        )
                    )
                )
                .filter(_solved_time__range=[interval_start, interval_end])
                .count()
            )
        else:
            solved = self.get_num_solved()

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

    def get_users_with_perm(self, perm):
        users_perms = get_users_with_perms(self, attach_perms=True)
        result = []
        for user, perms in users_perms.items():
            if perm in perms:
                result.append(user)

        return result


class HuntSettings(models.Model):
    hunt = models.OneToOneField(
        Hunt,
        on_delete=models.CASCADE,
        related_name="settings",
    )

    answer_queue_enabled = models.BooleanField(default=False)

    #
    # Google-specific settings
    #

    # The id of your Google Drive folder
    # This should be part of the URL (https://drive.google.com/drive/folders/<folder_id>)
    # This folder is used for login permissions and for puzzle storage.
    # This is where puzzle files will be kept, so it should not be modified by humans
    google_drive_folder_id = models.CharField(max_length=128, blank=True)

    # The id of your Google Sheets template file
    # This should be part of the url (https://docs.google.com/spreadsheets/d/<sheet_id>)
    google_sheets_template_file_id = models.CharField(max_length=128, blank=True)

    # The id of a Google Drive folder where template files for this hunt can be found
    # Used as a way to get around #372
    # Cardboard will try to use one of the files in here if possible, before making a copy
    # of the master sheet.
    # TODO: Figure out a better solution to this longer-term, like getting Drive permission on sign-in
    # and using those instead of the service account, or using an add-on somehow
    google_sheets_template_folder_id = models.CharField(max_length=128, blank=True)

    # A link to the Google Drive folder that solvers can use for misc. files
    google_drive_human_url = models.URLField(blank=True)

    #
    # Discord-specific settings
    #
    create_channel_by_default = models.BooleanField(
        default=True,
        help_text="Toggles whether puzzles should have chat channels created by default",
    )

    discord_guild_id = models.CharField(
        max_length=128,
        blank=True,
        help_text='The id of your Discord server. This can be found on the "Widget" page in the Server Settings',
    )

    discord_puzzle_announcements_channel_id = models.CharField(
        max_length=128,
        blank=True,
        help_text="""The id of the Discord channel to make puzzle announcements in.
        This channel can get noisy and is recommended to be its own separate channel.
        This ID can be found by enabling Developer Mode in Discord and right-clicking on the channel""",
    )

    discord_metas_category = models.CharField(
        max_length=128,
        default="metas",
        blank=True,
        help_text="The category name to create all metas in",
    )

    discord_unassigned_text_category = models.CharField(
        max_length=128,
        default="text [unassigned]",
        blank=True,
        help_text="The category name to create all unassigned Discord text channels in",
    )

    discord_unassigned_voice_category = models.CharField(
        max_length=128,
        default="voice [unassigned]",
        blank=True,
        help_text="The category name to create all unassigned Discord voice channels in",
    )

    discord_archive_category = models.CharField(
        max_length=128,
        default="archive",
        blank=True,
        help_text="The category name to archive all Discord channels for solved puzzles in",
    )

    discord_devs_role = models.CharField(
        max_length=128,
        default="dev",
        blank=True,
        help_text="The Discord role for the people maintaining the Cardboard instance, in case of problems",
    )

    active_user_lookback = models.DurationField(
        default=timedelta(minutes=10),
        help_text="Amount of time to look back for active users of a puzzle.",
    )
