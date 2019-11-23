from django.contrib import admin
from .models import Puzzle

class PuzzleAdmin(admin.ModelAdmin):
    pass

admin.site.register(Puzzle, PuzzleAdmin)
