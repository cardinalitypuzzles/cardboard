from django import template
from django.conf import settings
from puzzles.models import Puzzle, PuzzleTag
from puzzles.forms import StatusForm, MetaPuzzleForm, PuzzleForm, TagForm
from answers.forms import AnswerForm

DEFAULT_TAGS = [
    ('HIGH PRIORITY', PuzzleTag.RED),
    ('LOW PRIORITY', PuzzleTag.YELLOW),
    ('BACKSOLVED', PuzzleTag.BLUE)
]

register = template.Library()

def generate_sortkeys(puzzles):
    sortkey_dict = {}
    # TODO(asdfryan): This will fail if there are cycles. We should add cycle detection.
    def __get_sortkey(puzzle):
        def __get_status_sortkey(puzzle):
            ''' Unsolved puzzles should come before solved puzzles.'''
            if puzzle.is_solved():
                return "1-%s" % puzzle.pk
            return "0-%s" % puzzle.pk

        def __add_to_dict_and_return(pk, sortkey):
            sortkey_dict[pk] = sortkey
            print("sortkey for puzzle %s: %s" % (Puzzle.objects.get(id=pk).name, sortkey))
            return sortkey

        if puzzle.pk in sortkey_dict: return sortkey_dict[puzzle.pk]

        # If non-meta and has no assigned meta, it comes first.
        if not puzzle.is_meta and not puzzle.has_assigned_meta():
            return __add_to_dict_and_return(puzzle.pk, __get_status_sortkey(puzzle))

        # If it has an assigned meta puzzle, concatenate parent sortkey with current status sortkey.
        if puzzle.has_assigned_meta():
            print("metas length: %i" % len(puzzle.metas.all()))
            return __add_to_dict_and_return(puzzle.pk,
                "%s.%s" % (__get_sortkey(puzzle.metas.all()[0]), __get_status_sortkey(puzzle)))

        return __add_to_dict_and_return(puzzle.pk, "0.%s" % __get_status_sortkey(puzzle))

    for p in puzzles:
        __get_sortkey(p)

    return sortkey_dict

def table_status_class(puzzle):
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

@register.inclusion_tag('puzzles_table.html')
def get_table(puzzles, request):
    sortkeys = generate_sortkeys(puzzles)
    sorted_puzzles = sorted(puzzles, key=lambda p: sortkeys[p.pk])

    def __get_offset(puzzle):
        return max(0, 20 * sortkeys[puzzle.pk].count('-') - 1)

    status_forms = [StatusForm(initial={'status': p.status}) for p in sorted_puzzles]
    for (i, p) in enumerate(sorted_puzzles):
        if p.status in [Puzzle.SOLVED, Puzzle.PENDING]:
            status_forms[i].fields["status"].disabled = True
        else:
            status_forms[i].fields["status"].choices =\
                [(status, status) for status in Puzzle.VISIBLE_STATUS_CHOICES]

    meta_forms = [MetaPuzzleForm(initial={'metas': p.metas.all()}, instance=p) for p in sorted_puzzles]

    edit_forms = [PuzzleForm(initial={'name': p.name, 'url': p.url, 'is_meta': p.is_meta}) for p in sorted_puzzles]

    # this caches Puzzle.tags.all() for all the tag forms
    Puzzle.objects.all().prefetch_related('tags')
    tag_forms = [TagForm() for p in sorted_puzzles]

    # This is used for hierarchical formatting.
    offset = [__get_offset(p) for p in sorted_puzzles]

    puzzle_class = [table_status_class(p) for p in sorted_puzzles]

    context = {
        'rows': zip(sorted_puzzles, status_forms, meta_forms, edit_forms, tag_forms, offset, puzzle_class),
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



@register.inclusion_tag('show_tags.html')
def show_tags(puzzle, tag_form, request):
    all_tags = dict(
        DEFAULT_TAGS +
        [(t.name, t.color) for t in Puzzle.tags.all()]
    )
    current_tags = [(t.name, t.color) for t in puzzle.tags.all()]
    suggestions = [t for t in all_tags.items() if t not in current_tags]

    context = {
        'puzzle': puzzle,
        'current_tags': current_tags,
        'tag_form': tag_form,
        'suggestions': suggestions
    }
    return context
