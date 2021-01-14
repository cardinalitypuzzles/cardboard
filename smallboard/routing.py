from django.urls import re_path

from smallboard.consumers import NotificationConsumer

websocket_urlpatterns = [
    re_path(r"^notifications/(?P<hunt_pk>[0-9]+)$", NotificationConsumer.as_asgi()),
]
