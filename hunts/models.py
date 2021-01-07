from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
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

        # adds default start and end times if not provided
        if not self.start_time:
            self.start_time = self.created_on
            super().save(*args, **kwargs)
        if not self.end_time:
            self.end_time = self.start_time + timedelta(days=3)
            super().save(*args, **kwargs)
            
    @staticmethod
    def get_object_or_404(user=None, **kwargs):
        hunt = get_object_or_404(Hunt, **kwargs)
        if user and user.is_authenticated and user.last_accessed_hunt != hunt:
            user.last_accessed_hunt = hunt
            user.save(update_fields=["last_accessed_hunt"])
        return hunt
