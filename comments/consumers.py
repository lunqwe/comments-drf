from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
import json
from channels.db import database_sync_to_async
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework import mixins
from djangochannelsrestframework.observer.generics import (ObserverModelInstanceMixin, action)
from djangochannelsrestframework.observer import model_observer
from django.core.paginator import Paginator
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Comment
from .serializers import CommentSerializer, UserSerializer

User = get_user_model()

class WebsocketConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
    serializer_class = CommentSerializer
    authentication_classes = (JWTAuthentication, )
    
    async def connect(self):
        await self.channel_layer.group_add(
            'comments_group',
            self.channel_name
        )
        await self.accept()
        
    @sync_to_async()
    def load_comments(self, page_num, **kwargs):
        queryset = Comment.objects.all()
        paginator = Paginator(queryset, 50)
        result = paginator.get_page(page_num)
        comments = []
        for comment in result:
            comments.append({
                'user_name': comment.user_name,
                'email': comment.email,
                'text': comment.text
            })
        return comments
    
    @action()
    async def get_comments(self, page_num, **kwargs):
        comments = await self.load_comments(page_num=page_num)
        return await self.send(text_data=json.dumps({
            'event_type': 'display_comment',
            'comment': comments
        }))
        
    
    async def add_comment(self, event):
        comment = event['comment']
        await self.send(text_data=json.dumps({
            'event_type': 'display_comment',
            'comment': comment
        }))
            
    @action()
    async def logout(self, **kwargs):
        await self.channel_layer.group_discard(
            'comments_group',
            self.channel_name
        )
        await self.close(1000)
    
