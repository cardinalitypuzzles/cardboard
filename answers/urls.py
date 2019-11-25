from django.urls import path
from .views import AnswerView
from django.http import HttpResponseRedirect
from django.conf import settings

urlpatterns = [
    path("queue/<int:hunk_pk>", AnswerView.as_view()),
    path("queue/<int:hunk_pk>/<int:answer_pk>", AnswerView.as_view()),
    path('', lambda r: HttpResponseRedirect('queue/{}'.format(settings.ACTIVE_HUNT_ID)), name="queue"),
]