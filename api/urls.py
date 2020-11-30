from django.urls import path
from . import views

urlpatterns = [
    path("v1/hunt/<int:pk>/", views.HuntAPIView.as_view(), name="hunt_api_view"),
]
