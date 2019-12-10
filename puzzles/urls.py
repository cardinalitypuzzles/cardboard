from django.urls import path
from puzzles import views

urlpatterns = [
    path("<int:pk>/", views.index),
    path("update_status/<int:pk>/", views.update_status, name="update_status"),
    path("guess/<int:pk>/", views.guess, name="guess"),
    path("slack_guess/", views.slack_guess, name="slack_guess"),
    path("meta/<int:pk>/", views.set_metas),
    path("edit/<int:pk>/", views.edit_puzzle),
    path("delete/<int:pk>/", views.delete_puzzle),
]
