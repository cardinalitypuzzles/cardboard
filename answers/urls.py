from .views import AnswerView, answers, update_note
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import path

urlpatterns = [
    path("queue/<int:hunt_pk>", AnswerView.as_view()),
    path("queue/<int:hunt_pk>/answers", answers),
    path("queue/<int:hunt_pk>/<int:answer_pk>", AnswerView.as_view()),
    path("update_note/<int:answer_pk>", update_note, name="update_note"),
    path(
        "",
        lambda r: HttpResponseRedirect("queue/{}".format(settings.ACTIVE_HUNT_ID)),
        name="queue",
    ),
]
