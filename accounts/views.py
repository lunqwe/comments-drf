from django.http import Http404
from rest_framework import generics, serializers, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import User
from .serializers import (LoginSerializer,
                          SignUpSerializer,
                          UserSerializer,
                          )



# function for manage error details
def error_detail(e):
    errors = e.detail
    
    error_messages = []
    for field, messages in errors.items():
        error_messages.append(f'{field}: {messages[0].__str__()}')
    
    return error_messages

# function to get user`s new token
def get_user_jwt(user: User):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# login view
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                user = serializer.validated_data.get('user')
                tokens = get_user_jwt(user) # creating jwt tokens (refresh/access)
                return Response({
                    "detail": "You have been logged in successfully!",
                    'tokens': tokens
                }, status=status.HTTP_202_ACCEPTED)
            
        except serializers.ValidationError as e:
            data = {
                'status': 'error',
                'detail': error_detail(e)
                }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        
        
# sign up view    
class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            user_data = self.create(request, *args, **kwargs).data
            password = user_data.pop('password')
            user = User.objects.create(**user_data) # registering user
            user.set_password(password) # setting password
            user.save()
            tokens = get_user_jwt(user) # creating jwt tokens (refresh/access)
            
            return Response({
                'detail': "You have been registered successfully!",
                'tokens': tokens
            })
            
        # if serializer is not valid
        except serializers.ValidationError as e:
            data = {
                'status': 'error',
                'detail': error_detail(e)
                }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        
        
# user view for get/update object
class UserViewSet(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [IsAuthenticated, ]
    
    def get(self, request, *args, **kwargs):
        try: 
            user = self.get_object()
            if user.id == request.user.id:
                user_data = super().retrieve(request, *args, **kwargs).data
                return Response({
                    'data_type': "private",
                    'user': user_data # lets imagine there is something important xD
                })
            else:
                return Response({
                    'data_type': 'public',
                    'user': user.username # there could be some public data (username, image etc.)
                })
        except Http404:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        try:
            user_obj = self.get_object()
            if request.user.id == user_obj.id:
                super().update(request, *args, **kwargs)
                return Response({
                    'detail': 'User data updated successfully!'
                }, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({
                    'detail': "No permissions to change that user data."
                }, status=status.HTTP_403_FORBIDDEN)
        except Http404:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)