from django import template
from django.conf import settings
from puzzles.models import Puzzle, PuzzleTag
from puzzles.forms import StatusForm, MetaPuzzleForm, PuzzleForm, TagForm
from answers.forms import AnswerForm

DEFAULT_TAGS = [
    ('HIGH PRIORITY', PuzzleTag.RED),
    ('LOW PRIORITY', PuzzleTag.YELLOW),
    ('BACKSOLVED', PuzzleTag.GREEN),
    ('WORD', PuzzleTag.WHITE),
    ('LOGIC', PuzzleTag.WHITE),
    ('TECHNICAL', PuzzleTag.WHITE),
    ('SLOG', PuzzleTag.GRAY),
]

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

    # this caches Puzzle.tags.all() for all the tag forms
    Puzzle.objects.all().prefetch_related('tags')
    tag_forms = [TagForm() for p in puzzles]

    context = {
        'rows': zip(puzzles, status_forms, meta_forms, edit_forms, tag_forms),
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


@register.inclusion_tag('show_tags.html')
def show_tags(puzzle, tag_form, request):
    all_tags = dict(
        DEFAULT_TAGS +
        [(t.name, t.color) for t in Puzzle.tags.all()]
    )
    current_tags = [(t.name, t.color) for t in puzzle.tags.all()]
    suggestions = [t for t in all_tags.items() if t not in current_tags]
    suggestions.sort(key=lambda item: (PuzzleTag.COLOR_ORDERING[item[1]], item[0]))

    context = {
        'puzzle': puzzle,
        'current_tags': current_tags,
        'tag_form': tag_form,
        'suggestions': suggestions
    }
    return context
