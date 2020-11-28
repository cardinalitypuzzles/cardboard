from django.urls import path
from . import views

app_name = "hunts"
urlpatterns = [
    path("", views.index, name="index"),
    path("<slug:slug>/", views.HuntView.as_view(), name="all_puzzles"),
    path("<slug:slug>/puzzles", views.puzzles),
]
