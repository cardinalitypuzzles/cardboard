from .forms import UpdateAnswerNotesForm
from .forms import UpdateAnswerStatusForm
from .models import Answer
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.decorators.http import require_GET, require_POST
import google_api_lib
from hunts.models import Hunt
from puzzles.models import Puzzle

import logging

logger = logging.getLogger(__name__)


@require_POST
@login_required(login_url="/")
@transaction.atomic
def update_note(request, answer_pk):
    notes_form = UpdateAnswerNotesForm(request.POST)
    if notes_form.is_valid():
        answer = get_object_or_404(Answer.objects.select_for_update(), pk=answer_pk)
        notes_text = notes_form.cleaned_data["text"]
        answer.set_notes(notes_text)
    else:
        return JsonResponse(
            {"error": "Invalid notes form for answer with id %s" % answer_pk},
            status=400,
        )

    return JsonResponse({})


@require_GET
@login_required(login_url="/")
def answers(request, hunt_slug):
    hunt = Hunt.get_object_or_404(user=request.user, slug=hunt_slug)
    answer_objects = (
        Answer.objects.filter(puzzle__hunt__slug=hunt_slug)
        .prefetch_related("puzzle")
        .order_by("-created_on")
    )

    result = {
        "data": [
            [
                answer.created_on,
                answer.puzzle.name,
                answer.puzzle.url,
                answer.puzzle.is_meta,
                answer.text,
                answer.status,
                answer.id,
                answer.response,
            ]
            for answer in answer_objects
        ]
    }
    return JsonResponse(result)


class AnswerView(LoginRequiredMixin, View):
    login_url = "/"
    redirect_field_name = "next"

    def get(self, request, hunt_slug):
        hunt = Hunt.get_object_or_404(user=request.user, slug=hunt_slug)
        context = {
            "hunt_slug": hunt_slug,
            "hunt_name": hunt.name,
        }
        return render(request, "queue.html", context)

    def post(self, request, hunt_slug, answer_pk):
        """Handles answer status update"""
        status_form = UpdateAnswerStatusForm(request.POST)

        if status_form.is_valid():
            puzzle_already_solved = None
            status = None
            with transaction.atomic():
                guess = get_object_or_404(
                    Answer.objects.select_for_update(), pk=answer_pk
                )
                status = status_form.cleaned_data["status"]
                puzzle_already_solved = len(guess.puzzle.answer) > 0
                if status == Answer.CORRECT and puzzle_already_solved:
                    messages.warning(
                        request,
                        '{} was already marked as solved with the answer "{}"\n'.format(
                            guess.puzzle, guess.puzzle.answer
                        )
                        + "We won't stop ya, but please think twice.",
                    )

                guess.set_status(status)

            if puzzle_already_solved or status == Answer.CORRECT:
                metas = guess.puzzle.metas.all()
                for meta in metas:
                    google_api_lib.task.update_meta_sheet_feeders(meta)
        else:
            return JsonResponse(
                {
                    "error": "Invalid form for answer %s and hunt %s"
                    % (answer_pk, hunt_slug)
                },
                status=400,
            )

        return JsonResponse({})
