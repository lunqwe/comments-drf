from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework import mixins
from djangochannelsrestframework.observer.generics import (ObserverModelInstanceMixin, action)
from djangochannelsrestframework.observer import model_observer
from django.core.paginator import Paginator
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Comment
from .serializers import CommentSerializer, UserSerializer

User = get_user_model()

class WebsocketConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
    serializer_class = CommentSerializer
    authentication_classes = (JWTAuthentication, )
    
    async def connect(self):
        await self.accept()
    
    @action()
    async def add_comment(self, message, **kwargs):
        await self.send_json(message) 
            
    @action()
    async def logout(self, **kwargs):
        await self.close(1000)
    
