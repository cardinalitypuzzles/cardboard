from django.urls import path

from . import views

app_name = "hunts"
urlpatterns = [
    path("", views.index, name="index"),
    path("<slug:hunt_slug>/", views.ReactHuntView.as_view(), name="all_puzzles_react"),
    path("<slug:hunt_slug>/edit", views.edit, name="edit"),
    path("<slug:hunt_slug>/stats", views.stats, name="stats"),
    path("<slug:hunt_slug>/sync_discord_roles", views.sync_discord_roles, name="sync_discord_roles"),
    path("<slug:hunt_slug>/drive", views.redirect_to_drive, name="drive"),
]
