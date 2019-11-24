from django.urls import path
from puzzles import views

urlpatterns = [
    path("<int:pk>/", views.puzzle_page, name="puzzle_page"),
    path("update_status/<int:pk>/", views.update_status, name="update_status"),
    path("guess/<int:pk>/", views.guess, name="guess"),
]
