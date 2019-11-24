from django import template
from puzzles.models import Puzzle, MetaPuzzle
from puzzles.forms import StatusForm
from answers.forms import AnswerForm

register = template.Library()

@register.inclusion_tag('puzzles_table.html')
def get_table(puzzles, request):
    answers = []
    table_class = []
    badge = []

    for (i, p) in enumerate(puzzles):
        answers.append(p.answer if p.answer else "")

        if p.status == Puzzle.PENDING:
            table_class.append("table-warning")
        elif p.status == Puzzle.SOLVED:
            table_class.append("table-success")
        elif p.status == Puzzle.STUCK:
            table_class.append("table-danger")
        else:
            table_class.append("")



    status_forms = [StatusForm(initial={'status': p.status}) for p in puzzles]
    for (i, p) in enumerate(puzzles):
        if p.status in [Puzzle.SOLVED, Puzzle.PENDING]:
            status_forms[i].fields["status"].disabled = True

    answer_form = AnswerForm()
    return {'rows': zip(puzzles, answers, table_class, status_forms), 'guess_form': answer_form}


@register.inclusion_tag('title.html')
def get_title(puzzle):
    badge = ''
    if MetaPuzzle.objects.filter(pk=puzzle.pk).exists():
        badge = 'META'
    return {'puzzle': puzzle, 'badge': badge}


