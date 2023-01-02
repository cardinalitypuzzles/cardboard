from django.contrib import admin
from .models import Puzzle, PuzzleTag, PuzzleActivity
from answers.models import Answer


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


class PuzzleActivityAdmin(admin.ModelAdmin):
    list_display = ["user", "puzzle", "last_edit_time"]
    ordering = ("-last_edit_time",)


admin.site.register(Puzzle, PuzzleAdmin)
admin.site.register(PuzzleTag, PuzzleTagAdmin)
admin.site.register(PuzzleActivity, PuzzleActivityAdmin)
