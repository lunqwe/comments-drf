import time
from django.shortcuts import render
from rest_framework import generics, viewsets, mixins, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from celery.result import AsyncResult


from .models import Comment
from .serializers import CommentSerializer
from .tasks import create_comment, get_comments

def index(request):
    return render(request, 'index.html')


class AddCommentView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = (JWTAuthentication, )
        
    def perform_create(self, serializer):
        comment_data = serializer.validated_data
        user = self.request.user
        if user.is_authenticated:
            comment_data['created_by'] = user.username
            comment_data['email'] = user.email
            comment_data['owner'] = user
        create_comment.apply_async(args=[comment_data])
        

class CommentListView(generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def list(self, request, *args, **kwargs):
        page_number = request.query_params.get('page', 1)
        return Response(get_comments.apply_async(args=[page_number]).get())
        

class UpdateCommentView(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = (JWTAuthentication, )
    lookup_field = 'id'
    
    def put(self, request, *args, **kwargs):
        comment_obj = self.get_object()
        if comment_obj.owner == request.user:
            return self.update(request, *args, **kwargs)
        else:
            return Response('You are not owner of this comment', status=status.HTTP_403_FORBIDDEN)
    

    
    
    