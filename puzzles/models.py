from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save, post_save, pre_delete, m2m_changed
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
    # internal flag to know when to sync meta puzzles
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

    metas = models.ManyToManyField('self', symmetrical=False, related_name="feeders")

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


    def is_solved(self):
        return self.status == Puzzle.SOLVED


    def has_assigned_meta(self):
        return len(self.metas.all()) > 0


# Used for cycle detection before adding an edge from potential ancestor to child.
# We cannot have cycles, otherwise the PuzzleTree sorting will break.
def is_potential_ancestor(potential_ancestor, child):
    if child.pk == potential_ancestor.pk: return True
    if not child.has_assigned_meta(): False
    for parent in child.metas:
        if is_potential_ancestor(potential_ancestor, parent):
            True
    return False

# Hooks for syncing metas and tags
def update_tags_pre_save(sender, instance, **kwargs):
    if instance.is_meta:
        puzzles_needing_new_tag = []
        if instance.pk is not None:
            old_instance = Puzzle.objects.get(pk=instance.pk)
            if not old_instance.is_meta:
                puzzles_needing_new_tag = [instance]
            elif old_instance.name != instance.name:
                instance.tags.filter(name=old_instance.name).delete()
                puzzles_needing_new_tag = [instance] + list(instance.feeders.all())

        (new_tag, _) = PuzzleTag.objects.update_or_create(
            name=instance.name,
            defaults={'color' : PuzzleTag.BLACK, 'is_meta' : True},
        )

        for p in puzzles_needing_new_tag:
            p.tags.add(new_tag)

    else:
        PuzzleTag.objects.filter(name=instance.name).filter(is_meta=True).delete()


def update_tags_post_save(sender, instance, **kwargs):
    # make sure puzzles that already had tag now get assigned the meta
    # this has to happen post save, since instance has to exist first
    if instance.is_meta:
        puzzles_with_tag = Puzzle.objects.filter(tags__name__in=[instance.name]).exclude(name=instance.name)
        for p in puzzles_with_tag:
            p.metas.add(instance)
            p.save()


def update_tags_pre_delete(sender, instance, **kwargs):
    if instance.is_meta:
        PuzzleTag.objects.filter(name=instance.name).delete()


def update_tags_m2m(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == "post_add":
        for pk in pk_set:
            meta = Puzzle.objects.get(pk=pk)
            instance.tags.add(meta.name)
    elif action == "post_remove":
        for pk in pk_set:
            meta = Puzzle.objects.get(pk=pk)
            instance.tags.remove(meta.name)
    elif action == "post_clear":
        instance.tags.filter(is_meta=True).exclude(name=instance.name).remove()


pre_save.connect(update_tags_pre_save, sender=Puzzle)
post_save.connect(update_tags_post_save, sender=Puzzle)
pre_delete.connect(update_tags_pre_delete, sender=Puzzle)
m2m_changed.connect(update_tags_m2m, sender=Puzzle.metas.through)

def is_unassigned_channel(channel_id):
    '''
    Returns true if channel_id is not assigned to any Puzzle object.
    '''
    return not (Puzzle.objects.filter(channel=channel_id))
