from django.db import models
from puzzles.models import Puzzle

class Hunt(models.Model):
    name = models.CharField(max_length=128)
    url = models.URLField()
    created_on = models.DateTimeField(auto_now_add=True)
    puzzlers = models.ManyToManyField('accounts.Puzzler', related_name='hunts')
    active = models.BooleanField(default=True)
