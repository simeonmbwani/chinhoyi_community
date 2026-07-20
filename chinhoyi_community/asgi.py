"""
ASGI config for chinhoyi_community project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""
import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import messaging.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chinhoyi_community.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(messaging.routing.websocket_urlpatterns)
    ),
})