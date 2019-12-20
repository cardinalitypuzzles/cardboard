from .forms import UpdateAnswerNotesForm
from .forms import UpdateAnswerStatusForm
from .models import Answer
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import View
from hunts.models import Hunt
from puzzles.forms import PuzzleForm
from slack_lib.slack_client import SlackClient


@login_required(login_url='/accounts/login/')
def update_note(request, answer_pk):
    notes_form = UpdateAnswerNotesForm(request.POST)
    if notes_form.is_valid():
        answer = get_object_or_404(Answer, pk=answer_pk)
        notes_text = notes_form.cleaned_data["text"]
        answer.set_notes(notes_text)
        slack_client = SlackClient.getInstance()
        puzzle_channel = answer.puzzle.channel
        slack_client.send_message(puzzle_channel,
                                  "The operator has added an update regarding the answer "
                                   "\'%s\'. Note: \'%s\'" % (answer.text.upper(), notes_text))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class AnswerView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    def get(self, request, hunt_pk):
        hunt = get_object_or_404(Hunt, pk=hunt_pk)
        answers = Answer.objects.filter(puzzle__hunt__pk=hunt_pk).order_by('-created_on')
        status_forms = [UpdateAnswerStatusForm(initial={'status': ans.get_status()}) for ans in answers]
        notes_forms = [UpdateAnswerNotesForm(initial={'text': ans.get_notes()}) for ans in answers]

        context = {
            'hunt_pk': hunt_pk,
            'hunt_name': hunt.name,
            'rows' : zip(answers, status_forms, notes_forms)
        }
        return render(request, 'queue.html', context)

    @staticmethod
    def __update_slack_with_puzzle_status(answer, status):
        slack_client = SlackClient.getInstance()
        puzzle_channel = answer.puzzle.channel
        if status == Answer.PARTIAL:
            slack_client.send_message(puzzle_channel,
                                      "%s is PARTIALLY CORRECT!" %
                                      answer.text.upper())
        elif status == Answer.INCORRECT or status == Answer.CORRECT:
            slack_client.send_message(puzzle_channel, "%s is %s!" %
                                                      (answer.text.upper(), status))

        if status == Answer.CORRECT:
            slack_client.announce("%s has been solved with the answer: "
                                   "\'%s\' Hurray!" %
                                  (answer.puzzle.name, answer.text.upper()))


    def post(self, request, hunt_pk, answer_pk):
        status_form = UpdateAnswerStatusForm(request.POST)

        if status_form.is_valid():
            guess = get_object_or_404(Answer, pk=answer_pk)
            status = status_form.cleaned_data["status"]
            if status == Answer.CORRECT and len(guess.puzzle.answer) > 0:
                messages.warning(request,
                    '{} was already marked as solved with the answer "{}"\n'.format(guess.puzzle, guess.puzzle.answer) +
                    'We won\'t stop ya, but please think twice.')

            guess.set_status(status)
            self.__update_slack_with_puzzle_status(guess, status)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


