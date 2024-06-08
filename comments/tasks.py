from celery_app import app
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async
from django.core.paginator import Paginator

from comments.models import Comment
from comments.serializers import CommentSerializer


@app.task()
def create_comment(comment_data):
    comment = Comment.objects.create(**comment_data)
    comment_data = CommentSerializer(comment).data
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
    queryset = Comment.objects.all().order_by('created_at')
    paginator = Paginator(queryset, 25)
    result = paginator.get_page(page_num)
    comments = []
    for comment in result:
        comments.append({
            'id': comment.id,
            'username': comment.created_by,
            'email': comment.email,
            'text': comment.text
        })
    return comments