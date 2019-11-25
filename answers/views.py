from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views import View
from .models import Answer
from .forms import UpdateAnswerStatusForm
from hunts.models import Hunt


class AnswerView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    def get(self, request, hunk_pk):
        hunt = get_object_or_404(Hunt, pk=hunk_pk)
        answers = Answer.objects.filter(puzzle__hunt__pk=hunk_pk).order_by('-created_on')
        forms = [UpdateAnswerStatusForm(initial={'status': ans.get_status()}) for ans in answers]

        context = {
            'hunt_pk': hunk_pk,
            'hunt_name': hunt.name,
            'rows' : zip(answers, forms)
        }
        return render(request, 'queue.html', context)

    def post(self, request, hunk_pk, answer_pk):
        form = UpdateAnswerStatusForm(request.POST)

        if form.is_valid():
            answer = get_object_or_404(Answer, pk=answer_pk)
            answer.set_status(form.cleaned_data["status"])

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


