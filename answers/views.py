from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views import View
from .models import Answer
from .forms import UpdateAnswerNotesForm
from .forms import UpdateAnswerStatusForm
from hunts.models import Hunt


@login_required(login_url='/accounts/login/')
def update_note(request, answer_pk):
    notes_form = UpdateAnswerNotesForm(request.POST)
    if notes_form.is_valid():
        answer = get_object_or_404(Answer, pk=answer_pk)
        notes_text = notes_form.cleaned_data["text"]
        answer.set_notes(notes_text)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class AnswerView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    def get(self, request, hunk_pk):
        hunt = get_object_or_404(Hunt, pk=hunk_pk)
        answers = Answer.objects.filter(puzzle__hunt__pk=hunk_pk).order_by('-created_on')
        forms = [UpdateAnswerStatusForm(initial={'status': ans.get_status()}) for ans in answers]
        notes_forms = [UpdateAnswerNotesForm(initial={'text': ans.get_notes()}) for ans in answers]

        context = {
            'hunt_pk': hunk_pk,
            'hunt_name': hunt.name,
            'rows' : zip(answers, forms, notes_forms)
        }
        return render(request, 'queue.html', context)

    def post(self, request, hunk_pk, answer_pk):
        status_form = UpdateAnswerStatusForm(request.POST)

        if status_form.is_valid():
            guess = get_object_or_404(Answer, pk=answer_pk)
            status = status_form.cleaned_data["status"]
            if status == Answer.CORRECT and len(guess.puzzle.answer) > 0:
                messages.warning(request,
                    '{} was already marked as solved with the answer "{}"\n'.format(guess.puzzle, guess.puzzle.answer) +
                    'We won\'t stop ya, but please think twice.')

            guess.set_status(status)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


