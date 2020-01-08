from django import template
from django.conf import settings
from puzzles import tag_utils
from puzzles.models import Puzzle
from puzzles.puzzle_tree import PuzzleTree


register = template.Library()

# TODO(erwa): combine puzzles_table.html with all_puzzles.html
# and delete this file.
@register.inclusion_tag('puzzles_table.html')
def get_table(hunt_pk, request):
    context = {
        'slack_base_url': settings.SLACK_BASE_URL,
        'hunt_pk': hunt_pk,
    }
    return context
