from rest_framework import serializers

from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    to_comment_id = serializers.IntegerField(required=False)
    class Meta:
        model = Comment
        fields = ['id', 'created_by_username', 'email', 'text', 'owner', 'to_comment_id']
    
