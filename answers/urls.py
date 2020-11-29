from .views import AnswerView, answers, update_note
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import path

from hunts.views import LastAccessedHuntRedirectView

app_name = "answers"
urlpatterns = [
    path("queue/<slug:hunt_slug>", AnswerView.as_view(), name="submission_queue"),
    path("queue/<slug:hunt_slug>/answers", answers),
    path("queue/<slug:hunt_slug>/<int:answer_pk>", AnswerView.as_view()),
    path("update_note/<int:answer_pk>", update_note, name="update_note"),
    path(
        "",
        LastAccessedHuntRedirectView.as_view(pattern_name="answers:submission_queue"),
        name="queue",
    ),
]
