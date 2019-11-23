from django.shortcuts import render, redirect
from puzzles.models import Puzzle
from django.contrib.auth.decorators import login_required


@login_required(login_url='/accounts/login/')
def index(request):
    puzzles = Puzzle.objects.all()
    context = {
        'puzzles': puzzles
    }
    return render(request, 'index.html', context)


@login_required(login_url='/accounts/login/')
def puzzle_page(request, pk):
    puzzle = Puzzle.objects.get(pk=pk)
    context = {
        'puzzle': puzzle
    }
    return render(request, 'puzzle_page.html', context)