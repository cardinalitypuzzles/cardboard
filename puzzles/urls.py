from django.urls import path
from .views import redirect_to_sheet

app_name = "puzzles"
urlpatterns = [
    path("s/<int:puzzle_pk>", redirect_to_sheet, name="puzzle_sheet_redirect"),
]
