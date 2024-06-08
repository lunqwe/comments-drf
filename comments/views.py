import time
from django.shortcuts import render
from rest_framework import generics, viewsets, mixins
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from celery.result import AsyncResult


from .models import Comment
from .serializers import CommentSerializer
from .tasks import create_comment

def index(request):
    return render(request, 'index.html')


class AddCommentView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = (JWTAuthentication, )
        
    def perform_create(self, serializer):
        comment_data = serializer.validated_data
        create_comment.apply_async(args=[comment_data])
        
    

        



    
    
    