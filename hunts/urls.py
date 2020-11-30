from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:pk>/", views.HuntView.as_view(), name="all_puzzles"),
    path("<int:pk>/puzzles", views.puzzles),
]
