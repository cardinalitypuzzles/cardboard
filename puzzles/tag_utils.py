from .models import Puzzle
from .puzzle_tag import PuzzleTag

DEFAULT_TAGS = [
    ("HIGH PRIORITY", PuzzleTag.RED),
    ("LOW PRIORITY", PuzzleTag.YELLOW),
    ("BACKSOLVED", PuzzleTag.GREEN),
    ("WORD", PuzzleTag.WHITE),
    ("LOGIC", PuzzleTag.WHITE),
    ("TECHNICAL", PuzzleTag.WHITE),
    ("SLOG", PuzzleTag.GRAY),
    ("INTERACTIVE", PuzzleTag.BLUE),
]


def to_tag(tag_string):
    # Override default taggit behavior of splitting input string.
    return [tag_string.upper()]


def get_tags(puzzle):
    puzzle_tags = [[t.name, t.color] for t in puzzle.tags.all()]
    puzzle_tags.sort(key=lambda item: (PuzzleTag.color_ordering()[item[1]], item[0]))
    return puzzle_tags


def get_all_tags(hunt):
    all_tags = dict(
        DEFAULT_TAGS + [(t.name, t.color) for t in PuzzleTag.objects.filter(hunt=hunt)]
    )
    return all_tags
