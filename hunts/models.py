from django.core.exceptions import ValidationError
from django.contrib.staticfiles import finders
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from puzzles.models import Puzzle


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

    def validate_file_exists(value):
        if value and not finders.find(f"audio/{value}"):
            raise ValidationError(
                _("%(value)s is not an available audio file"),
                params={"value": value},
            )

    meta_sound = models.CharField(
        max_length=16,
        validators=[validate_file_exists],
        default=None,
        blank=True,
        null=True,
    )
    feeder_sound = models.CharField(
        max_length=16,
        validators=[validate_file_exists],
        default=None,
        blank=True,
        null=True,
    )

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

    def get_solves_per_hour(self):
        current_time = timezone.now()
        if self.end_time:
            current_time = min(current_time, self.end_time)
        if not self.start_time or self.start_time >= current_time:
            return "N/A"

        solved = self.get_num_solved()
        hours_elapsed = (current_time - self.start_time).total_seconds() / 3600
        return "{:.2f}".format(round(solved / hours_elapsed, 2))

    def get_minutes_per_solve(self):
        solved = self.get_num_solved()
        if solved == 0:
            return "N/A"

        current_time = timezone.now()
        if self.end_time:
            current_time = min(current_time, self.end_time)
        if not self.start_time or self.start_time >= current_time:
            return "N/A"

        minutes_elapsed = (current_time - self.start_time).total_seconds() / 60
        return "{:.2f}".format(round(minutes_elapsed / solved, 2))
