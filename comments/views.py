import time
from django.shortcuts import render
from django.http import Http404
from rest_framework import generics, serializers, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from celery.result import AsyncResult



from .models import Comment
from .serializers import CommentSerializer
from .tasks import create_comment, get_comments, update_comment, partial_update_comment
from accounts.views import error_detail

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
    permission_classes = [IsAuthenticated, ]
    lookup_field = 'id'
    
    def partial_update(self, request, *args, **kwargs):
        try:
            comment_obj = self.get_object()
            if comment_obj.owner == request.user:
                result = partial_update_comment.apply_async(args=[comment_obj.id, request.user.id, request.data])
                response_data = result.get()
                if 'error' in response_data:
                    return Response(response_data['error'], status=response_data['status'])
                return Response(response_data['comment'], status=status.HTTP_200_OK)
            else:
                return Response('You are not owner of this comment', status=status.HTTP_403_FORBIDDEN)
        except Http404:
            return Response('Comment not found', status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        try:
            comment_obj = self.get_object()
            if comment_obj.owner == request.user:
                result = update_comment.apply_async(args=[comment_obj.id, request.user.id, request.data])
                response_data = result.get()
                if 'error' in response_data:
                    return Response(response_data['error'], status=response_data['status'])
                return Response(response_data['comment'], status=status.HTTP_200_OK)
            else:
                return Response('You are not owner of this comment', status=status.HTTP_403_FORBIDDEN)
        except Http404:
            return Response('Comment not found', status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    
    