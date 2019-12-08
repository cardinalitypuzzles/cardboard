import os

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from .models import Puzzle
from .forms import StatusForm, MetaPuzzleForm
from answers.models import Answer
from answers.forms import AnswerForm



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
            answer_text = form.cleaned_data["text"].replace(' ', '').upper()
            # If answer has already been added to the queue
            if not Answer.objects.filter(puzzle=puzzle, text=answer_text):
                answer = Answer(text=answer_text, puzzle=puzzle)
                puzzle.status = Puzzle.PENDING
                answer.save()
                puzzle.save()
            else:
                messages.error(request, '"{}" has already been submitted as a guess'.format(answer_text))
        else:
            messages.error(request, form.errors)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@csrf_exempt
def slack_guess(request):
    if request.method == 'POST':
        print("request data: " + str(request.POST))
        slack_message = request.POST
        if slack_message.get('token') != os.environ.get("SLACK_VERIFICATION_TOKEN"):
            return HttpResponseForbidden()

        answer_text = slack_message.get('text')
        channel_id = slack_message.get('channel_id')
        puzzle = Puzzle.objects.get(channel=channel_id)
        print("puzzle: " + str(puzzle))
        if puzzle.status == Puzzle.SOLVED:
            return HttpResponse("Puzzle is already solved!")
        if Answer.objects.filter(puzzle=puzzle).filter(text=answer_text):
            return HttpResponse("The answer " + answer_text + " has already been submitted.")
        answer = Answer(text=answer_text, puzzle=puzzle)
        puzzle.status = Puzzle.PENDING
        answer.save()
        puzzle.save()

    return HttpResponse("Answer " + answer_text + " has been submitted!")


@login_required(login_url='/accounts/login/')
def set_metas(request, pk):
    if request.method == 'POST':
        form = MetaPuzzleForm(request.POST, instance=get_object_or_404(Puzzle, pk=pk))
        if form.is_valid():
            puzzle = get_object_or_404(Puzzle, pk=pk)
            metas = form.cleaned_data["metas"]
            puzzle.metas.set(metas)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
