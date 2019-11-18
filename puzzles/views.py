from django.shortcuts import render
from puzzles.models import Puzzle


def index(request):
    puzzles = Puzzle.objects.all()
    context = {
        'puzzles': puzzles
    }
    return render(request, 'index.html', context)


def puzzle_page(request, pk):
    puzzle = Puzzle.objects.get(pk=pk)
    context = {
        'puzzle': puzzle
    }
    return render(request, 'puzzle_page.html', context)