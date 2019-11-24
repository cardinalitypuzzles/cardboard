from django import template

register = template.Library()

@register.inclusion_tag('puzzles_table.html')
def get_table(puzzles):
    return {'puzzles': puzzles}