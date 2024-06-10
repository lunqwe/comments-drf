from rest_framework import serializers

from .models import User

class LoginSerializer(serializers.ModelSerializer):
    """ Serializer for login """
    
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
    """
    Serializer for creating user 
    Args:
        password2: required for confirm password

    Raises:
        serializers.ValidationError: if password didn`t match

    Returns:
        _type_: _description_
    """
    
    password2 = serializers.CharField(required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        
    def create(self, validated_data):
        # if passwords match
        if validated_data['password'] == validated_data['password2']:
            validated_data.pop('password2')
            return validated_data
        
        else:
            raise serializers.ValidationError('Passwords didn`t match')
        
        
class UserSerializer(serializers.ModelSerializer):
    """ Serializer for get/update user object """
    class Meta:
        model = User
        fields = ['id', 'username', 'email']