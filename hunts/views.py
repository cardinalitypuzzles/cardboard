import googleapiclient.discovery

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import View
from google.oauth2 import service_account

from .forms import HuntForm
from .models import Hunt
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


def create_google_sheets(name):
    if not hasattr(settings, 'GOOGLE_DRIVE_API_AUTHN_INFO'):
        return None

    credentials = service_account.Credentials.from_service_account_info(
        settings.GOOGLE_DRIVE_API_AUTHN_INFO,
        scopes=settings.GOOGLE_DRIVE_PERMISSIONS_SCOPES
    )

    service = googleapiclient.discovery.build('drive', 'v3', credentials=credentials)

    req_body = {
        'name': name
    }
    response = service.files().copy(
        fileId=settings.GOOGLE_SHEETS_TEMPLATE_FILE_ID,
        body=req_body,
        fields='webViewLink',
    ).execute()

    link = response['webViewLink']
    return link

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
            puzzle_url = form.cleaned_data["url"]
            sheets_url = create_google_sheets(name)
            # TODO(asdfryan): Don't create SlackClient every time we need it.
            slack_client = SlackClient()
            channel_id = slack_client.create_channel(name)
            channel_url = SlackClient.create_join_link(channel_id)
            if not sheets_url:
                sheets_url = puzzle_url

            if form.cleaned_data["is_meta"]:
                puzzle = MetaPuzzle(
                    name=name,
                    url=puzzle_url,
                    sheet=sheets_url,
                    channel=channel_url,
                    hunt=hunt,
                )
            else:
                puzzle = Puzzle(
                    name=name,
                    url=puzzle_url,
                    sheet=sheets_url,
                    channel=channel_url,
                    hunt=hunt,
                )
            puzzle.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

