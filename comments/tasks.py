from celery_app import app
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


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