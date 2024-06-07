from rest_framework import serializers


class CommentSerializer(serializers.Serializer):
    test = serializers.CharField()
    
class UserSerializer(serializers.Serializer):
    test = serializers.CharField()