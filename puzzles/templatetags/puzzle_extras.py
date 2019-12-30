from django import template
from django.conf import settings
from puzzles import tag_utils
from puzzles.models import Puzzle
from puzzles.puzzle_tree import PuzzleTree


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
        'rows': zip(sorted_puzzles, tags, metas, active_users, puzzle_class),
        'slack_base_url': settings.SLACK_BASE_URL,
    }
    return context


@register.inclusion_tag('title.html')
def get_title(puzzle):
    badge = ''
    if puzzle.is_meta:
        badge = 'META'
    context = {
        'puzzle': puzzle,
        'active_users': puzzle.active_users.all(),
        'badge': badge,
    }
    return context