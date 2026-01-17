import os
import django 


# Set your settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# Initialize Django
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from notifications.routing import websocket_urlpatterns
from notifications.middleware import JWTAuthMiddleware
from channels.security.websocket import AllowedHostsOriginValidator


# Standard ASGI app for HTTP
django_asgi_app = get_asgi_application()

# Channels routing for HTTP + WebSocket
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
