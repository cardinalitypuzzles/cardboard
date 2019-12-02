from django.db import models
from taggit.managers import TaggableManager

class Puzzle(models.Model):
    name = models.CharField(max_length=80, unique=True)
    hunt = models.ForeignKey('hunts.Hunt', on_delete=models.CASCADE, related_name='puzzles')
    url = models.URLField(unique=True)

    sheet = models.URLField(default='', unique=True)
    channel = models.CharField(max_length=128, default='', unique=True)
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

    tags = TaggableManager()

    def __str__(self):
        return self.name

    def set_answer(self, answer):
        self.answer = answer
        self.status = Puzzle.SOLVED
        self.save()

    def clear_answer(self):
        self.answer = ''
        self.status = Puzzle.SOLVING
        self.save()

    def get_tag_names(self):
        return ', '.join(self.tags.names())


class MetaPuzzle(Puzzle):
    feeders = models.ManyToManyField('Puzzle', related_name='metas')


def is_unassigned_channel(channel_id):
    '''
    Returns true if channel_id is not assigned to any Puzzle or MetaPuzzle object.
    '''
    return not (Puzzle.objects.filter(channel=channel_id) or
                MetaPuzzle.objects.filter(channel=channel_id))
