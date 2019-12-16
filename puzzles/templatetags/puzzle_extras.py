import cgi
from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
from puzzles.models import Puzzle
from puzzles.puzzle_tag import PuzzleTag
from puzzles.puzzle_tree import *
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
    sorted_np_pairs = PuzzleTree(puzzles).get_sorted_node_parent_pairs()
    sorted_puzzles = [pair.node.puzzle for pair in sorted_np_pairs]

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

    def __get_puzzle_class(sorted_np_pairs):
        puzzle_class = [table_status_class(pair.node.puzzle) for pair in sorted_np_pairs]
        most_recent_treegrid_id = {}
        for i, pair in enumerate(sorted_np_pairs):
            node = pair.node
            parent = pair.parent
            treegrid_id = i+1
            most_recent_treegrid_id[node.puzzle.pk] = treegrid_id
            puzzle_class[i] += " treegrid-%i" % treegrid_id
            if parent and parent.puzzle != None:
                # Most recently seen treegrid_id for parent
                parent_treegrid_id = most_recent_treegrid_id.get(parent.puzzle.pk, 0)
                if parent_treegrid_id > 0:
                    puzzle_class[i] += " treegrid-parent-%i" % parent_treegrid_id
            # If meta is solved, collapse the subtree.
            if len(node.children) > 0 and node.puzzle.is_solved():
                puzzle_class[i] += " initial-collapsed"
        return puzzle_class

    puzzle_class = __get_puzzle_class(sorted_np_pairs)

    context = {
        'rows': zip(sorted_puzzles, status_forms, meta_forms, edit_forms, tag_forms, puzzle_class),
        'guess_form': AnswerForm(),
        'slack_base_url': settings.SLACK_BASE_URL,
    }
    return context

@register.inclusion_tag('title.html')
def get_title(puzzle, edit_form):
    badge = ''
    if puzzle.is_meta:
        badge = 'META'
    context = {
        'puzzle': puzzle,
        'badge': badge,
        'edit_form': edit_form
    }
    return context

@register.inclusion_tag('assign_metas.html')
def assign_metas(puzzle, meta_form):
    context = {
        'puzzle': puzzle,
        'meta_form': meta_form
    }
    return context


@register.inclusion_tag('show_tags.html')
def show_tags(puzzle, tag_form, request):
    all_tags = dict(
        DEFAULT_TAGS +
        [(t.name, t.color) for t in Puzzle.tags.all()]
    )
    current_tags = [(t.name, t.color) for t in puzzle.tags.all()]
    current_tags.sort(key=lambda item: (PuzzleTag.COLOR_ORDERING[item[1]], item[0]))
    suggestions = [t for t in all_tags.items() if t not in current_tags]
    suggestions.sort(key=lambda item: (PuzzleTag.COLOR_ORDERING[item[1]], item[0]))

    context = {
        'puzzle': puzzle,
        'current_tags': current_tags,
        'tag_form': tag_form,
        'suggestions': suggestions
    }
    return context

@register.filter(name='escape')
@stringfilter
def escape(html):
    return cgi.escape(html)