from django.contrib import admin
from .models import Puzzle, MetaPuzzle

class PuzzleAdmin(admin.ModelAdmin):
    pass

class MetaPuzzleAdmin(admin.ModelAdmin):
    pass

admin.site.register(Puzzle, PuzzleAdmin)
admin.site.register(MetaPuzzle, MetaPuzzleAdmin)
