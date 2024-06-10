from rest_framework import serializers

from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'created_by_username', 'email', 'text', 'owner', 'to_comment']
    