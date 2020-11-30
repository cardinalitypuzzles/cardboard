from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from google_api_lib.google_api_client import GoogleApiClient
from taggit.managers import TaggableManager
from taggit.models import TagBase, GenericTaggedItemBase
from answers.models import Answer
from .puzzle_tag import PuzzleTagThrough


class PuzzleModelError(Exception):
    """Base class for puzzle exceptions"""

    pass


class DuplicatePuzzleNameError(PuzzleModelError):
    """Raised when there is a duplicate puzzle name is found."""

    pass


class DuplicatePuzzleUrlError(PuzzleModelError):
    """Raised when there is a duplicate puzzle url is found."""

    pass


class InvalidMetaPuzzleError(PuzzleModelError):
    """Raised when the meta status of a puzzle is invalid (i.e. cycles, dangling
    metas)."""

    pass


class Puzzle(models.Model):
    name = models.CharField(max_length=80, unique=True)
    hunt = models.ForeignKey(
        "hunts.Hunt", on_delete=models.CASCADE, related_name="puzzles"
    )
    url = models.URLField(blank=True)

    sheet = models.URLField(default="", unique=True)
    notes = models.TextField(default="")

    SOLVING = "SOLVING"
    PENDING = "PENDING"
    SOLVED = "SOLVED"
    STUCK = "STUCK"
    EXTRACTION = "EXTRACTION"
    ALL_STATUSES = [SOLVING, PENDING, SOLVED, STUCK, EXTRACTION]
    # Users should only be able to change status to one of these 3.
    VISIBLE_STATUS_CHOICES = [SOLVING, STUCK, EXTRACTION]

    status = models.CharField(
        max_length=10,
        choices=[(status, status) for status in ALL_STATUSES],
        default=SOLVING,
    )
    answer = models.CharField(max_length=128)

    tags = TaggableManager(through=PuzzleTagThrough)

    metas = models.ManyToManyField("self", symmetrical=False, related_name="feeders")

    is_meta = models.BooleanField(default=False)

    active_users = models.ManyToManyField(
        get_user_model(), related_name="active_puzzles"
    )

    def __str__(self):
        return self.name

    def update_metadata(self, new_name, new_url, new_is_meta):
        """
        Atomically updates the name/url/is_meta fields of the puzzle on valid
        input. Inputs are invalid if:
        * Another puzzle shares the same name or URL.
        * If new_is_meta is set to false, and another puzzle has an assigned
        * meta pointing to self.
        Raises exception on invalid input.
        """
        if (
            self.name == new_name
            and self.url == new_url
            and self.is_meta == new_is_meta
        ):
            return

        if self.name != new_name:
            if Puzzle.objects.filter(~Q(id=self.pk), Q(name=new_name)):
                raise DuplicatePuzzleNameError(
                    "Name %s is already taken by another puzzle." % new_name
                )

        is_new_url = False
        if self.url != new_url:
            is_new_url = True
            if Puzzle.objects.filter(~Q(id=self.pk), Q(url=new_url)):
                raise DuplicatePuzzleUrlError(
                    "URL %s is already taken by another puzzle." % new_url
                )

        # If previously a metapuzzle, but no longer one.
        if self.is_meta and not new_is_meta:
            # TODO(asdfryan): Consider auto-deleting the relevant meta
            # assignments instead of raising error.
            if Puzzle.objects.filter(metas__id=self.pk):
                raise InvalidMetaPuzzleError(
                    "Metapuzzles can only be deleted or made non-meta if no "
                    "other puzzles are assigned to it."
                )

        self.name = new_name
        self.url = new_url
        self.is_meta = new_is_meta

        self.save()

        if is_new_url:
            google_api_client = GoogleApiClient.getInstance()
            if google_api_client:
                google_api_client.add_puzzle_link_to_sheet(self.url, self.sheet)

    def set_answer(self, answer):
        self.answer = answer
        self.status = Puzzle.SOLVED
        self.save()

    def clear_answer(self, guess):
        # puzzle already solved by different guess, so this current guess does not affect state
        if self.status == Puzzle.SOLVED and self.answer != guess:
            return

        self.answer = ""
        if self.guesses.filter(Q(status=Answer.NEW) | Q(status=Answer.SUBMITTED)):
            self.status = Puzzle.PENDING
        else:
            self.status = Puzzle.SOLVING

        self.save()

    def is_solved(self):
        return self.status == Puzzle.SOLVED

    def has_assigned_meta(self):
        return len(self.metas.all()) > 0

    @staticmethod
    def maybe_truncate_name(name):
        max_allowed_length = Puzzle._meta.get_field("name").max_length
        return name[:max_allowed_length]


# Used for cycle detection before adding an edge from potential ancestor to child.
# We cannot have cycles, otherwise the PuzzleTree sorting will break.
def is_ancestor(potential_ancestor, child):
    if child.pk == potential_ancestor.pk:
        return True
    if not child.has_assigned_meta():
        False
    for parent in child.metas.all():
        if is_ancestor(potential_ancestor, parent):
            return True
    return False
