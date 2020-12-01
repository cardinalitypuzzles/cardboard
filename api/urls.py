from django.urls import path
from . import views

urlpatterns = [
    path("v1/hunt/<int:pk>", views.HuntAPIView.as_view(), name="hunt_api_view"),
    path(
        "v1/hunt/<int:pk>/puzzles", views.AllPuzzles.as_view(), name="all_puzzles_api"
    ),
]
