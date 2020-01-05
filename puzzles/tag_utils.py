from .models import Puzzle
from .puzzle_tag import PuzzleTag

DEFAULT_TAGS = [
    ('HIGH PRIORITY', PuzzleTag.RED),
    ('LOW PRIORITY', PuzzleTag.YELLOW),
    ('BACKSOLVED', PuzzleTag.GREEN),
    ('WORD', PuzzleTag.WHITE),
    ('LOGIC', PuzzleTag.WHITE),
    ('TECHNICAL', PuzzleTag.WHITE),
    ('SLOG', PuzzleTag.GRAY),
]


def to_tag(tag_string):
    # Override default taggit behavior of splitting input string.
    return [tag_string.upper()]


def get_tags(puzzle):
    puzzle_tags = [[t.name, t.color] for t in puzzle.tags.all()]
    puzzle_tags.sort(key=lambda item: (PuzzleTag.COLOR_ORDERING[item[1]], item[0]))
    return puzzle_tags


def get_all_tags():
    all_tags = dict(
        DEFAULT_TAGS +
        [(t.name, t.color) for t in Puzzle.tags.all()]
    )
    return all_tags