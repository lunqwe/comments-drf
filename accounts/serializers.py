from rest_framework import serializers

from .models import User

class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'password']

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        
        if not user.check_password(password):
            raise serializers.ValidationError("Wrong password.")
        
        data['user'] = user
        return data
    
class SignUpSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        
    def create(self, validated_data):
        if validated_data['password'] == validated_data['password2']:
            validated_data.pop('password2')
            return validated_data
        
        else:
            raise serializers.ValidationError('Passwords didn`t match')
        
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']