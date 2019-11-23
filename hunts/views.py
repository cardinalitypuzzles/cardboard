from django.shortcuts import render
from .models import Hunt
from .forms import HuntForm
from django.contrib.auth.decorators import login_required


@login_required(login_url='/accounts/login/')
def index(request):
    if request.method == 'POST':
        form = HuntForm(request.POST)
        if form.is_valid():
            hunt = Hunt(
                name=form.cleaned_data["name"],
                url=form.cleaned_data["url"]
            )
            hunt.save()

    context = {
        'active_hunts': Hunt.objects.filter(active=True).order_by('-created_on'),
        'finished_hunts': Hunt.objects.filter(active=False).order_by('-created_on'),
        'form': form
    }
    return render(request, 'index.html', context)



@login_required(login_url='/accounts/login/')
def all_puzzles(request, pk):
    hunt = Hunt.objects.get(pk=pk)
    context = {
        'hunt_name': hunt.name,
        'puzzles': hunt.puzzles.all()
    }
    return render(request, 'all_puzzles.html', context)