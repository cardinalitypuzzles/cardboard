from django.shortcuts import render, redirect
from .models import Puzzle
from .forms import PuzzleForm
from django.contrib.auth.decorators import login_required


@login_required(login_url='/accounts/login/')
def puzzle_page(request, pk):
    if request.method == 'POST':
        form = PuzzleForm(request.POST)
        if form.is_valid():
            Puzzle = Puzzle(
                name=form.cleaned_data["name"],
                url=form.cleaned_data["url"]
            )
            Puzzle.save()

    puzzle = Puzzle.objects.get(pk=pk)
    context = {
        'puzzle': puzzle
    }
    return render(request, 'puzzle_page.html', context)