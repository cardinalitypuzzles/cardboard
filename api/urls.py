from django.urls import path
from . import views

puzzle_list = views.PuzzleViewSet.as_view(
    {
        "get": "list",
        "post": "create",
    }
)

puzzle_detail = views.PuzzleViewSet.as_view(
    {
        "get": "retrieve",
        "delete": "destroy",
        "patch": "partial_update",
    }
)

urlpatterns = [
    path("v1/hunt/<int:pk>", views.HuntAPIView.as_view(), name="hunt_api_view"),
    path("v1/hunt/<int:hunt_id>/puzzles", puzzle_list, name="puzzle_list"),
    path("v1/hunt/<int:hunt_id>/puzzles/<int:pk>", puzzle_detail, name="puzzle_detail"),
]
