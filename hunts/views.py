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

    def __handle_dup_puzzle(self, request):
        message = "A puzzle with the given name or url already exists!"
        messages.error(request, message)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    def post(self, request, pk):
        hunt = get_object_or_404(Hunt, pk=pk)
        form = PuzzleForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data["name"]
            puzzle_url = url_normalize(form.cleaned_data["url"])
            is_meta = form.cleaned_data["is_meta"]

            puzzle_class = MetaPuzzle if is_meta else Puzzle

            # Early termination -- if a puzzle with given name or URL exists, don't try to create
            # a new sheet or slack channel. This is purely an optimization to avoid dangling
            # google sheets / slack channels.
            already_exists = (Puzzle.objects.filter(Q(name=name) | Q(url=puzzle_url)).exists() or
                             MetaPuzzle.objects.filter(Q(name=name) | Q(url=puzzle_url)).exists())
            if already_exists:
                return self.__handle_dup_puzzle(request)

            # TODO(erwaman): Add error handling and refactor into google drive lib.
            google_drive_client = GoogleDriveClient.getInstance()
            if google_drive_client:
                sheet = google_drive_client.create_google_sheets(name)
            else:
                # TODO(erwaman): This should incur a warning.
                sheet = puzzle_url

            # TODO(asdfryan): Add error handling and refactor into slack lib.
            slack_client = SlackClient.getInstance()
            channel_id = slack_client.create_or_join_channel(name)
            if channel_id is None:
                messages.warning(request, "Slack channel not created")

            try:
                puzzle_class.objects.create(
                    name=name,
                    url=puzzle_url,
                    hunt=hunt,
                    sheet=sheet,
                    channel=channel_id if channel_id else name
                )
                # Announce new puzzle is available on slack.
                slack_client.announce_puzzle_creation(name, channel_id, is_meta)

            except IntegrityError as e:
                # TODO(asdfryan): Think about cleaning up dangling sheets / slack channels.
                # TODO(asdfryan): Think about other catchable errors.
                return self.__handle_dup_puzzle(request)
        else:
            messages.error(request, "Puzzle not created because the form was invalid.")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

