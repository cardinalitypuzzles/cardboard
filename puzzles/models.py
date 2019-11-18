from django.db import models

class Puzzle(models.Model):
    name = models.CharField(max_length=128)
    url = models.URLField()

    sheet = models.URLField()
    channel = models.URLField()
    notes = models.TextField()

    NEW = "NEW"
    SOLVED = "SOLVED"
    STUCK = "STUCK"
    STATUS_CHOICES = [NEW, SOLVED, STUCK]

    status = models.CharField(
        max_length=10,
        choices=[(status, status) for status in STATUS_CHOICES],
        default=NEW)