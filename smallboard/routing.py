from django.urls import re_path

from smallboard.asgi import django_asgi_app
from smallboard.consumers import NotificationConsumer

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    re_path(
                        r"^notifications/(?P<hunt_pk>[0-9]+)$",
                        NotificationConsumer.as_asgi(),
                    ),
                ]
            )
        ),
    }
)
