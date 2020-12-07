from django.urls import path
from . import views

puzzle_list = views.PuzzleViewSet.as_view(
    {
        "get": "list",
    }
)

urlpatterns = [
    path("v1/hunt/<int:pk>", views.HuntAPIView.as_view(), name="hunt_api_view"),
    path("v1/hunt/<int:hunt_id>/puzzles", puzzle_list, name="puzzle_list"),
]
