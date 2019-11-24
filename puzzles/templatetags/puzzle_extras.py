from django import template
from puzzles.models import Puzzle

register = template.Library()

@register.inclusion_tag('puzzles_table.html')
def get_table(puzzles):
    cls = []
    for p in puzzles:
        if p.status == Puzzle.PENDING:
            cls.append("table-warning")
        elif p.status == Puzzle.SOLVED:
            cls.append("table-success")
        elif p.status == Puzzle.STUCK:
            cls.append("table-danger")
        else:
            cls.append("")

    return {'puzzles_with_class': zip(puzzles, cls)}