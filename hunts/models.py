from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from puzzles.models import Puzzle


class Hunt(models.Model):
    name = models.CharField(max_length=128)
    url = models.URLField()
    created_on = models.DateTimeField(auto_now_add=True)
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
