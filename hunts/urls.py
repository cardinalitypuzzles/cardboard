from django.urls import path
from . import views

app_name = "hunts"
urlpatterns = [
    path("", views.index, name="index"),
    path("<slug:hunt_slug>/", views.ReactHuntView.as_view(), name="all_puzzles_react"),
    path("<slug:hunt_slug>/stats", views.stats, name="stats"),
    path("<slug:hunt_slug>/drive", views.redirect_to_drive, name="drive"),
]
