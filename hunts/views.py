from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import View

from url_normalize import url_normalize

from .forms import HuntForm
from .models import Hunt
from google_drive_lib.google_drive_client import GoogleDriveClient
from puzzles.forms import PuzzleForm
from puzzles.models import Puzzle, MetaPuzzle
from slack_lib.slack_client import SlackClient


@login_required(login_url='/accounts/login/')
def index(request):
    form = HuntForm()

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


class HuntView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    def get(self, request, pk):
        if not Hunt.objects.filter(pk=pk).exists():
            return index(request)

        hunt = get_object_or_404(Hunt, pk=pk)
        form = PuzzleForm()
        context = {
            'request': request,
            'hunt_name': hunt.name,
            'hunt_pk': pk,
            'puzzles': hunt.puzzles.all(),
            'form': form
        }
        return render(request, 'all_puzzles.html', context)

    def post(self, request, pk):
        hunt = get_object_or_404(Hunt, pk=pk)
        form = PuzzleForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data["name"]
            puzzle_url = url_normalize(form.cleaned_data["url"])

            puzzle_class = Puzzle
            if form.cleaned_data["is_meta"]:
                puzzle_class = MetaPuzzle

            try:
                (puzzle, created) = puzzle_class.objects.get_or_create(
                    name=name,
                    url=puzzle_url,
                    hunt=hunt,
                )
            except IntegrityError as e:
                # puzzle creation may still fail if (name, puzzle_url) as a pair is unique
                # but the fields individually are not
                duplicates = puzzle_class.objects.filter(Q(name=name) | Q(url=puzzle_url))
                if duplicates.exists():
                    puzzle = duplicates.first()
                    created = False
                else:
                    messages.error(request,  "Puzzle not created:\n" + e.args)
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

            if created:
                google_drive_client = GoogleDriveClient.getInstance()
                if google_drive_client:
                    puzzle.sheet = google_drive_client.create_google_sheets(name)
                else:
                    puzzle.sheet = puzzle_url

                slack_client = SlackClient.getInstance()
                puzzle.channel = slack_client.create_channel(name)
                if not puzzle.channel:
                    puzzle.channel = name
                puzzle.save()
            else:
                message = "Puzzle not created: duplicate entry found\n"
                message += "Sheet: " + puzzle.sheet + "\n"
                message += "Slack: https://slack.com/app_redirect?channel={}".format(puzzle.channel)
                messages.error(request, message)
        else:
            messages.error(request, "Puzzle not created:")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

