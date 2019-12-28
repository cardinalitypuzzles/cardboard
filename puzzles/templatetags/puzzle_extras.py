import cgi
from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
from puzzles import tag_utils
from puzzles.models import Puzzle
from puzzles.puzzle_tree import *
from puzzles.forms import StatusForm, MetaPuzzleForm, PuzzleForm, TagForm
from answers.forms import AnswerForm



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

    tags = [tag_utils.get_tags(p) for p in sorted_puzzles]
    metas = [list(p.metas.values('name')) for p in sorted_puzzles]
    active_users = [p.active_users.all() for p in sorted_puzzles]

    status_forms = [StatusForm(initial={'status': p.status},
                               auto_id=False) for p in sorted_puzzles]
    for (i, p) in enumerate(sorted_puzzles):
        if p.status in [Puzzle.SOLVED, Puzzle.PENDING]:
            status_forms[i].fields["status"].disabled = True
        else:
            status_forms[i].fields["status"].choices =\
                [(status, status) for status in Puzzle.VISIBLE_STATUS_CHOICES]

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
        'rows': zip(sorted_puzzles, tags, metas, active_users, status_forms, puzzle_class),
        'guess_form': AnswerForm(auto_id=False),
        'slack_base_url': settings.SLACK_BASE_URL,
    }
    return context

@register.inclusion_tag('title.html')
def get_title(puzzle):
    context = {
        'puzzle': puzzle,
        'active_users': list(puzzle.active_users.all()),
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
def show_tags(puzzle):
    puzzle_tags = tag_utils.get_tags(puzzle)
    context = {
        'puzzle': puzzle,
        'current_tags': puzzle_tags,
    }
    return context


@register.filter(name='escape')
@stringfilter
def escape(html):
    return cgi.escape(html)

