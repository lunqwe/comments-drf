from django.shortcuts import render
from django.http import Http404
from django.db import transaction
from rest_framework import generics, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response

from .models import Comment
from .serializers import CommentSerializer
from .tasks import create_comment, get_comments, update_comment, partial_update_comment, clear_comments_cache


def index(request):
    return render(request, 'index.html') # index.html is a functionality preview of websocket


# create comment view
class AddCommentView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = (JWTAuthentication, )
    
    @transaction.atomic
    def perform_create(self, serializer):
        comment_data = serializer.validated_data
        user = self.request.user
        if user.is_authenticated:
            comment_data['created_by'] = user.username
            comment_data['email'] = user.email
            comment_data['owner'] = user 
            
        if 'file' in comment_data:
            file = comment_data.pop('file')
            
        comment = create_comment.apply_async(args=[comment_data]).get()# starting celery function that creates and notifies websocket 
        comment.file = file
        comment.save()
        
        
# get comments view
class CommentListView(generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def list(self, request, *args, **kwargs):
        page_number = request.query_params.get('page', 1)
        return Response(get_comments.apply_async(args=[page_number]).get()) # starting celery task
        

# update comment view
class UpdateCommentView(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = (JWTAuthentication, )
    lookup_field = 'id'
    
    def partial_update(self, request, *args, **kwargs):
        try:
            comment_obj = self.get_object()
            if comment_obj.owner == request.user: # checking using jwtauthentication
                result = partial_update_comment.apply_async(args=[comment_obj.id, request.user.id, request.data])
                response_data = result.get()
                if 'error' in response_data:
                    return Response(response_data['error'], status=response_data['status'])
                clear_comments_cache() # if updated - clearing cache
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
                clear_comments_cache() # if updated - clearing cache 
                return Response(response_data['comment'], status=status.HTTP_200_OK)
            else:
                return Response('You are not owner of this comment', status=status.HTTP_403_FORBIDDEN)
        except Http404:
            return Response('Comment not found', status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    
    