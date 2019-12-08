from django.db import models
from django.db.models import Q
from taggit.managers import TaggableManager
from answers.models import Answer

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
    EXTRACTION = 'EXTRACTION'
    ALL_STATUSES = [SOLVING, PENDING, SOLVED, STUCK, EXTRACTION]
    # Users should only be able to change status to one of these 3.
    VISIBLE_STATUS_CHOICES = [SOLVING, STUCK, EXTRACTION]

    status = models.CharField(
        max_length=10,
        choices=[(status, status) for status in ALL_STATUSES],
        default=SOLVING)
    answer = models.CharField(max_length=128)

    tags = TaggableManager()

    metas = models.ManyToManyField('self') 

    is_meta = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def set_answer(self, answer):
        self.answer = answer
        self.status = Puzzle.SOLVED
        self.save()

    def clear_answer(self, guess):
        # puzzle already solved by different guess, so this current guess does not affect state
        if self.status == Puzzle.SOLVED and self.answer != guess:
            return

        self.answer = ''
        if self.guesses.filter(Q(status=Answer.NEW) | Q(status=Answer.SUBMITTED)):
            self.status = Puzzle.PENDING
        else:
            self.status = Puzzle.SOLVING

        self.save()

    def get_tag_names(self):
        return ', '.join(self.tags.names())


def is_unassigned_channel(channel_id):
    '''
    Returns true if channel_id is not assigned to any Puzzle object.
    '''
    return not (Puzzle.objects.filter(channel=channel_id))
