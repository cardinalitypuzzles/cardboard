from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import Q
from django.dispatch import receiver

from answers.models import Answer
from .puzzle_tag import PuzzleTag


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
    name = models.CharField(max_length=80)
    hunt = models.ForeignKey(
        "hunts.Hunt", on_delete=models.CASCADE, related_name="puzzles"
    )
    url = models.URLField(blank=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    notes = models.TextField(default="")
    sheet = models.URLField(default=None, unique=True, null=True, blank=True)

    SOLVING = "SOLVING"
    PENDING = "PENDING"  # Only supported when answer_queue_enabled is True
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

    # Deprecated. Use guesses instead (see answers/models.py) which points to an Answer
    # object.
    answer = models.CharField(max_length=128)

    BACKSOLVED_TAG = "BACKSOLVED"

    tags = models.ManyToManyField(PuzzleTag, related_name="puzzles")

    metas = models.ManyToManyField("self", symmetrical=False, related_name="feeders")

    is_meta = models.BooleanField(default=False)

    active_users = models.ManyToManyField(
        get_user_model(), related_name="active_puzzles"
    )

    chat_room = models.OneToOneField(
        "chat.ChatRoom", on_delete=models.SET_NULL, null=True
    )

    discord_channel_id = models.CharField(
        max_length=50, unique=True, blank=True, null=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "hunt"], name="unique_names_per_hunt"
            ),
        ]

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
            if Puzzle.objects.filter(
                ~Q(id=self.pk), Q(hunt=self.hunt), Q(name=new_name)
            ):
                raise DuplicatePuzzleNameError(
                    "Name %s is already taken by another puzzle." % new_name
                )

        if self.url != new_url:
            if Puzzle.objects.filter(~Q(id=self.pk), Q(hunt=self.hunt), Q(url=new_url)):
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

    def solved_time(self):
        if not self.is_solved():
            return None
        return (
            self.guesses.filter(status=Answer.CORRECT).latest("created_on").created_on
        )

    def has_assigned_meta(self):
        return len(self.metas.all()) > 0

    def can_delete(self):
        return not (self.is_meta and Puzzle.objects.filter(metas__id=self.pk))

    def correct_answers(self):
        return sorted(
            [answer.text for answer in self.guesses.filter(status=Answer.CORRECT)]
        )

    def create_field_url_map(self):
        """
        Creates dictionary mapping text -> url for all relevant urls if they exist.
        """
        field_url_map = {}
        field_url_map["Puzzle"] = self.url
        if self.chat_room:
            if self.chat_room.text_channel_url:
                field_url_map["Text Channel"] = self.chat_room.text_channel_url
            if self.chat_room.audio_channel_url:
                field_url_map["Voice Channel"] = self.chat_room.audio_channel_url
        if self.sheet:
            field_url_map["Sheet"] = self.sheet

        return field_url_map

    def is_backsolved(self):
        return self.tags.filter(name=Puzzle.BACKSOLVED_TAG, hunt=self.hunt).exists()

    @staticmethod
    def maybe_truncate_name(name):
        max_allowed_length = Puzzle._meta.get_field("name").max_length
        return name[:max_allowed_length]


@receiver(models.signals.post_delete, sender=Puzzle)
def delete_chat_room(sender, instance, using, **kwargs):
    if instance.chat_room:
        instance.chat_room.delete()


# Used for cycle detection before adding an edge from potential ancestor to child.
# We cannot have cycles, otherwise the sorting will break.
def is_ancestor(potential_ancestor, child):
    if child.pk == potential_ancestor.pk:
        return True
    if not child.has_assigned_meta():
        False
    for parent in child.metas.all():
        if is_ancestor(potential_ancestor, parent):
            return True
    return False
