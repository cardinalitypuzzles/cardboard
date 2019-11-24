from django.contrib import admin
from .models import Puzzle, MetaPuzzle
from answers.models import Answer

class AnswerInline(admin.TabularInline):
    model = Answer

class PuzzleAdmin(admin.ModelAdmin):
    inlines = [
        AnswerInline,
    ]

class MetaPuzzleAdmin(admin.ModelAdmin):
    inlines = [
        AnswerInline,
    ]

admin.site.register(Puzzle, PuzzleAdmin)
admin.site.register(MetaPuzzle, MetaPuzzleAdmin)
