from django.contrib import admin
from .models import Puzzle
from answers.models import Answer


class AnswerInline(admin.TabularInline):
    model = Answer


class PuzzleAdmin(admin.ModelAdmin):
    inlines = [
        AnswerInline,
    ]


admin.site.register(Puzzle, PuzzleAdmin)
