from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Puzzle
from puzzles.forms import StatusForm
from django.http import HttpResponseRedirect

@login_required(login_url='/accounts/login/')
def puzzle_page(request, pk):
    puzzle = Puzzle.objects.get(pk=pk)
    context = {
        'puzzle': puzzle,
        'form': form
    }
    return render(request, 'puzzle_page.html', context)


@login_required(login_url='/accounts/login/')
def update_status(request, pk):
    if request.method == 'POST':
        form = StatusForm(request.POST, instance=Puzzle.objects.get(pk=pk))
        if form.is_valid():
            form.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))