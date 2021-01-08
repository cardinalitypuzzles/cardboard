from django.urls import path
from . import views

app_name = "hunts"
urlpatterns = [
    path("", views.index, name="index"),
    path("<slug:hunt_slug>/", views.ReactHuntView.as_view(), name="all_puzzles_react"),
    path(
        "nonreact/<slug:hunt_slug>/",
        views.HuntView.as_view(),
        name="all_puzzles",
    ),
    path("<slug:hunt_slug>/puzzles", views.puzzles),
    path("<slug:hunt_slug>/stats", views.stats, name="stats"),
]
