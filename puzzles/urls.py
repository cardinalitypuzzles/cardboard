from django.urls import path

from .views import puzzle_frame

app_name = "puzzles"
urlpatterns = [
    path("s/<int:puzzle_pk>", puzzle_frame, name="puzzle_frame"),
]
