from django.contrib.auth import get_user_model
from django.db import models
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
