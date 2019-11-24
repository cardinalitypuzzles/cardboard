from django import template
from answers.models import Answer

register = template.Library()

@register.simple_tag
def answer_class(answer):
    status = answer.get_status()
    if status == Answer.SUBMITTED:
        return "table-warning"
    elif status == Answer.CORRECT:
        return "table-success"
    elif status == Answer.INCORRECT:
        return "table-danger"
    else:
        return ""