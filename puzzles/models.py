from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, pre_delete
from taggit.managers import TaggableManager
from taggit.models import TagBase, GenericTaggedItemBase
from answers.models import Answer

class PuzzleModelError(Exception):
    '''Base class for puzzle exceptions'''
    pass


class DuplicatePuzzleNameError(PuzzleModelError):
    '''Raised when there is a duplicate puzzle name is found.'''
    pass


class DuplicatePuzzleUrlError(PuzzleModelError):
    '''Raised when there is a duplicate puzzle url is found.'''
    pass

class InvalidMetaPuzzleError(PuzzleModelError):
    '''Raised when the meta status of a puzzle is invalid (i.e. cycles, dangling
    metas).'''
    pass


class PuzzleTag(TagBase):
    BLUE = "primary"
    GRAY = "secondary"
    GREEN = "success"
    RED = "danger"
    YELLOW = "warning"
    WHITE = "light"
    BLACK = "dark"
    COLORS = [
        (BLUE, "blue"),
        (GRAY, "gray"),
        (GREEN, "green"),
        (RED, "red"),
        (YELLOW, "yellow"),
        (WHITE, "white"),
        (BLACK, "black")
    ]
    COLOR_ORDERING = {
        RED: 0,
        BLACK: 1,
        WHITE: 2,
        GRAY: 3,
        BLUE: 4,
        GREEN: 5,
        YELLOW: 6
    }
    color = models.CharField(
        max_length=10,
        choices=COLORS,
        default=BLUE)
    is_meta = models.BooleanField(default=False)


class PuzzleTagThrough(GenericTaggedItemBase):
    tag = models.ForeignKey(
        PuzzleTag,
        on_delete=models.CASCADE,
        related_name="tagged_items",
    )


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

    tags = TaggableManager(through=PuzzleTagThrough)

    metas = models.ManyToManyField('self', symmetrical=False)

    is_meta = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def update_metadata(self, new_name, new_url, new_is_meta):
        '''
        Atomically updates the name/url/is_meta fields of the puzzle on valid
        input. Inputs are invalid if:
        * Another puzzle shares the same name or URL.
        * If new_is_meta is set to false, and another puzzle has an assigned
        * meta pointing to self.
        Raises exception on invalid input.
        '''
        if self.name == new_name and self.url == new_url and self.is_meta == new_is_meta:
            return

        if self.name != new_name:
            if Puzzle.objects.filter(~Q(id=self.pk), Q(name=new_name)):
                raise DuplicatePuzzleNameError(
                    "Name %s is already taken by another puzzle." % new_name)

        if self.url != new_url:
            if Puzzle.objects.filter(~Q(id=self.pk), Q(url=new_url)):
                raise DuplicatePuzzleUrlError(
                    "URL %s is already taken by another puzzle." % new_url)

        # If previously a metapuzzle, but no longer one.
        if self.is_meta and not new_is_meta:
            # TODO(asdfryan): Consider auto-deleting the relevant meta
            # assignments instead of raising error.
            if (Puzzle.objects.filter(metas__id=self.pk)):
                raise InvalidMetaPuzzleError(
                    "Metapuzzles can only be deleted or made non-meta if no "
                    "other puzzles are assigned to it.")

        self.name = new_name
        self.url = new_url
        self.is_meta = new_is_meta

        self.save()


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


def update_tags_post_save(sender, instance, **kwargs):
    if instance.is_meta:
        defunct_tag = instance.tags.filter(is_meta=True).exclude(name=instance.name)
        if defunct_tag.exists():
            defunct_tag = defunct_tag.get()
            puzzles_needing_new_tag = list(Puzzle.objects.filter(tags__name__in=[defunct_tag.name]))
            defunct_tag.delete()
        else:
            puzzles_needing_new_tag = [instance]

        (new_tag, _) = PuzzleTag.objects.update_or_create(
            name=instance.name,
            defaults={'color' : PuzzleTag.BLACK, 'is_meta' : True},
        )

        # make sure puzzles that already had tag now get assigned the meta
        puzzles_with_tag = Puzzle.objects.filter(tags__name__in=[instance.name]).exclude(name=instance.name)
        for p in puzzles_with_tag:
            p.metas.add(instance)
            p.save()

        for p in puzzles_needing_new_tag:
            p.tags.add(new_tag)

    else:
        PuzzleTag.objects.filter(name=instance.name).filter(is_meta=True).delete()


def update_tags_pre_delete(sender, instance, **kwargs):
    if instance.is_meta:
        PuzzleTag.objects.filter(name=instance.name).delete()


post_save.connect(update_tags_post_save, sender=Puzzle)
pre_delete.connect(update_tags_pre_delete, sender=Puzzle)

def is_unassigned_channel(channel_id):
    '''
    Returns true if channel_id is not assigned to any Puzzle object.
    '''
    return not (Puzzle.objects.filter(channel=channel_id))
