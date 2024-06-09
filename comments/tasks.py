from celery_app import app
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async
from django.core.paginator import Paginator
from django.http import Http404
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from django.core.cache import cache

from .models import Comment
from .serializers import CommentSerializer

def clear_comments_cache():
    cache_keys_to_clear = [
        f'comments_page_{page_num}'
        for page_num in range(1, 100)  # Указать максимальное количество страниц
    ]
    cache.delete_many(cache_keys_to_clear)


@app.task()
def create_comment(comment_data):
    comment = Comment.objects.create(**comment_data)
    comment_data = CommentSerializer(comment).data
    clear_comments_cache()
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
            'comments_group',
            {
                'type': 'add_comment',
                'comment': comment_data
            }
        )
    
@app.task()
def get_comments(page_num):
    cache_key = f'comments_page_{page_num}'
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    queryset = Comment.objects.all().order_by('created_at')[::-1]
    paginator = Paginator(queryset, 25)
    result = paginator.get_page(page_num)
    comments = []
    for comment in result:
        comments.append({
            'id': comment.id,
            'username': comment.created_by_username,
            'email': comment.email,
            'text': comment.text
        })
        
    cache.set(cache_key, comments, timeout=3600)
    return comments



@app.task()
def update_comment(comment_id, user_id, data):
    try:
        with transaction.atomic():
            comment_obj = Comment.objects.select_for_update().get(id=comment_id)
            if comment_obj.owner_id == user_id:
                serializer = CommentSerializer(comment_obj, data=data)
                if serializer.is_valid():
                    serializer.save()
                    return {'comment': serializer.data, 'status': status.HTTP_200_OK}
                else:
                    return {'error': serializer.errors, 'status': status.HTTP_400_BAD_REQUEST}
            else:
                return {'error': 'You are not owner of this comment', 'status': status.HTTP_403_FORBIDDEN}
    except Comment.DoesNotExist:
        return {'error': 'Comment not found', 'status': status.HTTP_404_NOT_FOUND}

@app.task()
def partial_update_comment(comment_id, user_id, data):
    try:
        with transaction.atomic():
            comment_obj = Comment.objects.select_for_update().get(id=comment_id)
            if comment_obj.owner_id == user_id:
                serializer = CommentSerializer(comment_obj, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return {'comment': serializer.data, 'status': status.HTTP_200_OK}
                else:
                    return {'error': serializer.errors, 'status': status.HTTP_400_BAD_REQUEST}
            else:
                return {'error': 'You are not owner of this comment', 'status': status.HTTP_403_FORBIDDEN}
    except Comment.DoesNotExist:
        return {'error': 'Comment not found', 'status': status.HTTP_404_NOT_FOUND}