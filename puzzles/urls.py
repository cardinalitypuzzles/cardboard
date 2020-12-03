from django.urls import path
from puzzles import views

urlpatterns = [
    path("<slug:hunt_slug>/", views.index),
    path("update_status/<int:pk>/", views.update_status, name="update_status"),
    path("guess/<int:pk>/", views.guess, name="guess"),
    path("meta/<int:pk>/", views.set_metas),
    path("edit/<int:pk>/", views.edit_puzzle),
    path("delete/<int:pk>/", views.delete_puzzle),
    path("add_tag/<int:pk>/", views.add_tag),
    path("add_tags_form/<int:pk>", views.add_tags_form),
    path("remove_tag/<int:pk>/<str:tag_text>", views.remove_tag),
    path("meta_select_form/<int:pk>", views.meta_select_form),
]
