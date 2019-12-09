from django import template
from django.conf import settings
from puzzles.models import Puzzle
from puzzles.forms import StatusForm, MetaPuzzleForm, PuzzleForm
from answers.forms import AnswerForm

register = template.Library()

@register.inclusion_tag('puzzles_table.html')
def get_table(puzzles, request):
    status_forms = [StatusForm(initial={'status': p.status}) for p in puzzles]
    for (i, p) in enumerate(puzzles):
        if p.status in [Puzzle.SOLVED, Puzzle.PENDING]:
            status_forms[i].fields["status"].disabled = True
        else:
            status_forms[i].fields["status"].choices =\
                [(status, status) for status in Puzzle.VISIBLE_STATUS_CHOICES]

    meta_forms = [MetaPuzzleForm(initial={'metas': p.metas.all()}, instance=p) for p in puzzles]

    edit_forms = [PuzzleForm(initial={'name': p.name, 'url': p.url, 'is_meta': p.is_meta}) for p in puzzles]

    context = {
        'rows': zip(puzzles, status_forms, meta_forms, edit_forms),
        'guess_form': AnswerForm(),
        'slack_base_url': settings.SLACK_BASE_URL,
    }
    return context

@register.inclusion_tag('title.html')
def get_title(puzzle):
    badge = ''
    if puzzle.is_meta:
        badge = 'META'
    return {'puzzle': puzzle, 'badge': badge}


@register.simple_tag
def puzzle_class(puzzle):
    if puzzle.status == Puzzle.PENDING:
        return "table-warning"
    elif puzzle.status == Puzzle.EXTRACTION:
        return "table-danger"
    elif puzzle.status == Puzzle.SOLVED:
        return "table-success"
    elif puzzle.status == Puzzle.STUCK:
        return "table-danger"
    else:
        return ""
