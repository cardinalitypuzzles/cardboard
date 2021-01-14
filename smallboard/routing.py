from django.urls import re_path

from smallboard.consumers import NotificationConsumer

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator



application = ProtocolTypeRouter(
    {
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    [
                        re_path(
                            r"^notifications/(?P<hunt_pk>[0-9]+)$",
                            NotificationConsumer.as_asgi(),
                        ),
                    ]
                )
            )
        ),
    }
)
