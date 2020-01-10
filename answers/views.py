from .forms import UpdateAnswerNotesForm
from .forms import UpdateAnswerStatusForm
from .models import Answer
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.decorators.http import require_GET, require_POST
from hunts.models import Hunt
from puzzles.forms import PuzzleForm
from puzzles.models import Puzzle
from slack_lib.slack_client import SlackClient

import logging

logger = logging.getLogger(__name__)


@require_POST
@login_required(login_url='/accounts/login/')
@transaction.atomic
def update_note(request, answer_pk):
    notes_form = UpdateAnswerNotesForm(request.POST)
    if notes_form.is_valid():
        answer = get_object_or_404(Answer.objects.select_for_update(), pk=answer_pk)
        notes_text = notes_form.cleaned_data["text"]
        answer.set_notes(notes_text)
        slack_client = SlackClient.getInstance()
        puzzle_channel = answer.puzzle.channel
        slack_client.send_message(puzzle_channel,
                                  "The operator has added an update regarding the answer "
                                   "\'%s\'. Note: \'%s\'" % (answer.text.upper(), notes_text))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@require_GET
@login_required(login_url='/accounts/login/')
def answers(request, hunt_pk):
    hunt = get_object_or_404(Hunt, pk=hunt_pk)
    answer_objects = Answer.objects.filter(puzzle__hunt__pk=hunt_pk).prefetch_related('puzzle').order_by('-created_on')

    result = {
        "data": [
            [
                answer.created_on, answer.puzzle.name,
                answer.puzzle.url, answer.puzzle.is_meta, answer.text,
                answer.status, answer.id, answer.response,
            ]
            for answer in answer_objects
        ]
    }
    return JsonResponse(result)


class AnswerView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    def get(self, request, hunt_pk):
        hunt = get_object_or_404(Hunt, pk=hunt_pk)
        context = {
            'hunt_pk': hunt_pk,
            'hunt_name': hunt.name,
        }
        return render(request, 'queue.html', context)

    # TODO(erwa): Move this method out of AnswerView, as this is being used from
    # puzzles/views.py as well
    @staticmethod
    def update_slack_with_puzzle_status(answer, status):
        '''
        Sends Slack messages about answer status updates and archives/unarchives
        puzzle channels accordingly
        '''
        slack_client = SlackClient.getInstance()
        puzzle_channel = answer.puzzle.channel
        message = ''
        if status == Answer.NEW:
            message = ("NEW answer '%s' has been guessed for puzzle '%s'."
                       % (answer.text, answer.puzzle.name))
        elif status == Answer.SUBMITTED:
            message = ("'%s' has been SUBMITTED for puzzle '%s' on the hunt website."
                       % (answer.text, answer.puzzle.name))
        elif status in [Answer.PARTIAL, Answer.INCORRECT, Answer.CORRECT]:
            message = ("'%s' for puzzle '%s' is %s!"
                       % (answer.text, answer.puzzle.name, status))
        else:
            logger.error("Unexpected status '%s' for answer '%s' for puzzle '%s'"
                         % (status, answer.text, answer.puzzle.name))
            return

        slack_client.unarchive_channel(puzzle_channel)
        slack_client.send_message(puzzle_channel, message)
        slack_client.send_answer_queue_message(message)
        if status == Answer.CORRECT:
            slack_client.announce("'%s' has been solved with the answer: "
                                  "\'%s\' Hurray!"
                                  % (answer.puzzle.name, answer.text))
            slack_client.archive_channel(puzzle_channel)
        elif answer.puzzle.status == Puzzle.SOLVED:
            # puzzle was already solved from another guess
            slack_client.archive_channel(puzzle_channel)

    @transaction.atomic
    def post(self, request, hunt_pk, answer_pk):
        """Handles answer status update"""
        status_form = UpdateAnswerStatusForm(request.POST)

        status_code = 200
        if status_form.is_valid():
            guess = get_object_or_404(Answer.objects.select_for_update(), pk=answer_pk)
            status = status_form.cleaned_data["status"]
            if status == Answer.CORRECT and len(guess.puzzle.answer) > 0:
                messages.warning(request,
                    '{} was already marked as solved with the answer "{}"\n'.format(guess.puzzle, guess.puzzle.answer) +
                    'We won\'t stop ya, but please think twice.')

            guess.set_status(status)
            self.update_slack_with_puzzle_status(guess, status)
        else:
            logger.warn('invalid form for answer ' + str(answer_pk) + ' and hunt ' + str(hunt_pk))
            status_code = 400

        return JsonResponse({}, status=status_code)
