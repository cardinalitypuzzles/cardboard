from django import template
from django.template.defaultfilters import stringfilter
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
    elif status == Answer.PARTIAL:
        return "table-warning"
    else:
        return ""

@register.filter
@stringfilter
def strip(value):
    return value.replace(" ", "")
