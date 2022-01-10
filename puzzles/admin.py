from django.contrib import admin
from .models import Puzzle
from answers.models import Answer


class AnswerInline(admin.TabularInline):
    model = Answer


class PuzzleAdmin(admin.ModelAdmin):
    list_display = ["name", "is_meta", "hunt", "status", "answer"]
    list_filter = ["hunt", "is_meta"]
    inlines = [
        AnswerInline,
    ]


admin.site.register(Puzzle, PuzzleAdmin)
