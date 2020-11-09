from .views import AnswerView, answers, update_note
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import path

from hunts.views import ActiveHuntRedirectView

app_name = "answers"
urlpatterns = [
    path("queue/<int:hunt_pk>", AnswerView.as_view(), name="hunt_queue"),
    path("queue/<int:hunt_pk>/answers", answers),
    path("queue/<int:hunt_pk>/<int:answer_pk>", AnswerView.as_view()),
    path("update_note/<int:answer_pk>", update_note, name="update_note"),
    path(
        "",
        ActiveHuntRedirectView.as_view(pattern_name="answers:hunt_queue"),
        name="queue",
    ),
]
