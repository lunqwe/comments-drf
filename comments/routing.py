from django.urls import path, re_path

from .consumers import WebsocketConsumer


websocket_urlpatterns = [
    path('ws/comments/', WebsocketConsumer.as_asgi()),
]