from django.shortcuts import render
from .models import Puzzle
from django.contrib.auth.decorators import login_required

@login_required(login_url='/accounts/login/')
def puzzle_page(request, pk):
    puzzle = Puzzle.objects.get(pk=pk)
    context = {
        'puzzle': puzzle,
        'form': form
    }
    return render(request, 'puzzle_page.html', context)

