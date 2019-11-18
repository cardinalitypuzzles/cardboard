from django.urls import path
from puzzles import views

urlpatterns = [
    path('', views.index, name='index'),
    path("<int:pk>/", views.puzzle_page, name="puzzle_page"),
]
