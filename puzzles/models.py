from django.db import models

class Puzzle(models.Model):
    name = models.CharField(max_length=80, unique=True)
    hunt = models.ForeignKey('hunts.Hunt', on_delete=models.CASCADE, related_name='puzzles')
    url = models.URLField(unique=True)

    sheet = models.URLField(default='')
    channel = models.CharField(max_length=128, default='')
    notes = models.TextField(default='')

    SOLVING = 'SOLVING'
    PENDING = 'PENDING'
    SOLVED = 'SOLVED'
    STUCK = 'STUCK'
    STATUS_CHOICES = [SOLVING, PENDING, SOLVED, STUCK]

    status = models.CharField(
        max_length=10,
        choices=[(status, status) for status in STATUS_CHOICES],
        default=SOLVING)
    answer = models.CharField(max_length=128)

    def set_answer(self, answer):
        self.answer = answer
        self.status = Puzzle.SOLVED
        self.save()

    def clear_answer(self):
        self.answer = ''
        self.status = Puzzle.SOLVING
        self.save()

class MetaPuzzle(Puzzle):
    feeders = models.ManyToManyField('Puzzle', related_name='metas')
