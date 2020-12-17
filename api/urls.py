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

answer = views.AnswerViewSet.as_view(
    {
        "post": "create",
    }
)

answer_edit = views.AnswerViewSet.as_view(
    {
        "delete": "destroy",
        "patch": "partial_update",
    }
)

tag_detail = views.PuzzleTagViewSet.as_view(
    {
        "get": "retrieve",
        "delete": "destroy",
    }
)

urlpatterns = [
    path("v1/hunt/<int:pk>", views.HuntAPIView.as_view(), name="hunt_api_view"),
    path("v1/hunt/<int:hunt_id>/puzzles", puzzle_list, name="puzzle_list"),
    path("v1/hunt/<int:hunt_id>/puzzles/<int:pk>", puzzle_detail, name="puzzle_detail"),
    path("v1/hunt/<int:hunt_id>/puzzles/<int:puzzle_id>/answer", answer, name="answer"),
    path(
        "v1/hunt/<int:hunt_id>/puzzles/<int:puzzle_id>/answer/<int:pk>",
        answer_edit,
        name="answer_edit",
    ),
    path(
        "v1/hunt/<int:hunt_id>/puzzles/<int:puzzle_id>/tags/<int:pk>",
        tag_detail,
        name="tag_detail",
    ),
]
