from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Puzzle
from .forms import StatusForm, MetaPuzzleForm
from answers.models import Answer
from answers.forms import AnswerForm
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt


@login_required(login_url='/accounts/login/')
def index(request, pk):
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/hunts/{}'.format(pk)))


@login_required(login_url='/accounts/login/')
def update_status(request, pk):
    if request.method == 'POST':
        form = StatusForm(request.POST, instance=get_object_or_404(Puzzle, pk=pk))
        if form.is_valid():
            form.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='/accounts/login/')
def guess(request, pk):
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        puzzle = get_object_or_404(Puzzle, pk=pk)

        if form.is_valid() and puzzle.status != Puzzle.SOLVED:
            answer = Answer(text=form.cleaned_data["text"], puzzle=puzzle)
            puzzle.status = Puzzle.PENDING
            answer.save()
            puzzle.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@csrf_exempt
def slack_guess(request):
    if request.method == 'POST':
        print("request data: " + str(request.POST))
        slack_message = request.POST

        if slack_message.get('token') != os.environ.get("SLACK_API_TOKEN"):
            return HttpResponseForbidden()
    return HttpResponse(status=200)


@login_required(login_url='/accounts/login/')
def set_metas(request, pk):
    if request.method == 'POST':
        form = MetaPuzzleForm(request.POST)
        if form.is_valid():
            puzzle = get_object_or_404(Puzzle, pk=pk)
            metas = form.cleaned_data["meta_select"]
            puzzle.metas.set(metas)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
