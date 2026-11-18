from django.urls import path

from . import views

hunt_detail = views.HuntViewSet.as_view(
    {
        "get": "retrieve",
    }
)

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

answer_list = views.AnswerViewSet.as_view(
    {
        "post": "create",
    }
)

answer_detail = views.AnswerViewSet.as_view(
    {
        "delete": "destroy",
        "patch": "partial_update",
    }
)

tag_list = views.PuzzleTagViewSet.as_view(
    {
        "post": "create",
    }
)

notes_detail = views.PuzzleNotesView.as_view(
    {
        "post": "update",
    }
)

tag_detail = views.PuzzleTagViewSet.as_view(
    {
        "get": "retrieve",
        "delete": "destroy",
    }
)

urlpatterns = [
    path("v1/hunts/<int:pk>", hunt_detail, name="hunt_detail"),
    path("v1/hunts/<int:hunt_id>/puzzles", puzzle_list, name="puzzle_list"),
    path(
        "v1/hunts/<int:hunt_id>/puzzles/<int:pk>", puzzle_detail, name="puzzle_detail"
    ),
    path(
        "v1/puzzles/<int:puzzle_id>/answers",
        answer_list,
        name="answer_list",
    ),
    path(
        "v1/puzzles/<int:puzzle_id>/answers/<int:pk>",
        answer_detail,
        name="answer_detail",
    ),
    path("v1/puzzles/<int:puzzle_id>/notes", notes_detail, name="notes_detail"),
    path("v1/puzzles/<int:puzzle_id>/tags", tag_list, name="tag_list"),
    path(
        "v1/puzzles/<int:puzzle_id>/tags/<int:pk>",
        tag_detail,
        name="tag_detail",
    ),
]
