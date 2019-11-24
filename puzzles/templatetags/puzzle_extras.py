from django import template
from puzzles.models import Puzzle
from puzzles.forms import StatusForm

register = template.Library()

@register.inclusion_tag('puzzles_table.html')
def get_table(puzzles, request):
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

    status_forms = [StatusForm(initial={'status': p.status}) for p in puzzles]
    return {'rows': zip(puzzles, cls, status_forms)}


