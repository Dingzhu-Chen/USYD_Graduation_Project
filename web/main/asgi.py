"""
ASGI config for main project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/asgi/
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')


from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from channels.layers import get_channel_layer
from notification import consumers as notificationConsumers
from main.consumers import DisasterNotificationConsumer as disasterConsumers

application = get_asgi_application()

# Define the Channel Layer
channel_layer = get_channel_layer()

application = ProtocolTypeRouter({
    'http': application,
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path("ws/disasterNotification/", disasterConsumers.as_asgi(), name="disasterNotification"),
                path('ws/notification/', notificationConsumers.NotificationConsumer.as_asgi(), name="notification"),
                ]
        )
    ),
})
