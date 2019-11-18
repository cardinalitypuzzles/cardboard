from django.urls import path
from puzzles import views

urlpatterns = [
    path('', views.index, name='index'),
]
