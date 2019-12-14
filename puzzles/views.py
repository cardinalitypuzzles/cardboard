import os

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from url_normalize import url_normalize

from .models import *
from .forms import StatusForm, MetaPuzzleForm, PuzzleForm, TagForm
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

@login_required(login_url='/accounts/login/')
def edit_puzzle(request, pk):
    if request.method == 'POST':
        form = PuzzleForm(request.POST)
        if form.is_valid():
            new_name = form.cleaned_data["name"]
            new_url = url_normalize(form.cleaned_data["url"])
            new_is_meta = form.cleaned_data["is_meta"]
            puzzle = get_object_or_404(Puzzle, pk=pk)
            try:
                puzzle.update_metadata(new_name, new_url, new_is_meta)
                # TODO(asdfryan): Consider also renaming the slack channel to match the
                # new puzzle name.
            except (DuplicatePuzzleNameError, DuplicatePuzzleUrlError, InvalidMetaPuzzleError) as e:
               messages.error(request, str(e))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='/accounts/login/')
def delete_puzzle(request, pk):
    if request.method == 'POST':
        puzzle = get_object_or_404(Puzzle, pk=pk)
        if puzzle.is_meta and Puzzle.objects.filter(metas__id=pk):
            messages.error(request,
                "Metapuzzles can only be deleted or made non-meta if no "
                "other puzzles are assigned to it.")
        else:
            puzzle.delete()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='/accounts/login/')
def add_tag(request, pk):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            puzzle = get_object_or_404(Puzzle, pk=pk)
            (tag, _) = PuzzleTag.objects.update_or_create(
                name=form.cleaned_data["name"],
                defaults={'color' : form.cleaned_data["color"]}
            )
            puzzle.tags.add(tag)
        else:
            messages.error(request, form)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='/accounts/login/')
def remove_tag(request, pk, tag):
    if request.method == 'POST':
        puzzle = get_object_or_404(Puzzle, pk=pk)
        if puzzle.tags.filter(name=tag).exists():
            puzzle.tags.remove(tag)
        else:
            messages.error(request, "Could not find tag to remove")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
