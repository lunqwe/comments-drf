from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
import json
from channels.db import database_sync_to_async
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework import mixins
from djangochannelsrestframework.observer.generics import (ObserverModelInstanceMixin, action)
from djangochannelsrestframework.observer import model_observer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Comment
from .serializers import CommentSerializer
from .tasks import get_comments

User = get_user_model()

class WebsocketConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
    
    serializer_class = CommentSerializer
    authentication_classes = (JWTAuthentication, )
    
    #default action to connect websocket
    async def connect(self):
        await self.channel_layer.group_add(
            'comments_group',
            self.channel_name
        )
        await self.accept()
        
    
    # action for load comments
    @action()
    async def get_comments(self, page_num: int, **kwargs):
        comments = get_comments.apply_async(args=[page_num]) # celery task to load data from db

        return await self.send(text_data=json.dumps({
            'event_type': 'display_comment',
            'comment': comments.get()
        }))
        
    # create comment function (not @action because of api endpoint)
    async def add_comment(self, event: dict):
        comment = event['comment']
        await self.send(text_data=json.dumps({
            'event_type': 'display_comment',
            'comment': comment
        }))
    
    # action for close websocket connection
    @action()
    async def logout(self, **kwargs):
        await self.channel_layer.group_discard(
            'comments_group',
            self.channel_name
        )
        await self.close(1000)
    
