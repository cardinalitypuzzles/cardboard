from django.contrib.auth import get_user_model
from django.db import models
from puzzles.models import Puzzle

class Hunt(models.Model):
    name = models.CharField(max_length=128)
    url = models.URLField()
    created_on = models.DateTimeField(auto_now_add=True)
    puzzlers = models.ManyToManyField(get_user_model(), related_name='hunts')
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
