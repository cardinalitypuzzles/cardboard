from django.contrib import admin

from answers.models import Answer

from .models import Puzzle, PuzzleTag


class AnswerInline(admin.TabularInline):
    model = Answer


class PuzzleAdmin(admin.ModelAdmin):
    list_display = ["name", "is_meta", "hunt", "status", "answer"]
    list_filter = ["hunt", "is_meta"]
    inlines = [
        AnswerInline,
    ]


class PuzzleTagAdmin(admin.ModelAdmin):
    list_display = ["hunt", "name", "color", "is_meta"]
    list_filter = ["hunt", "is_meta"]


admin.site.register(Puzzle, PuzzleAdmin)
admin.site.register(PuzzleTag, PuzzleTagAdmin)
