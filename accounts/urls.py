from django.urls import path
from .views import SignUpView, LoginView, UserViewSet


urlpatterns = [
    path('register', SignUpView.as_view(), name='create_user'),
    path('login', LoginView.as_view(), name='login'),
    path('user/<int:pk>', UserViewSet.as_view(), name='get_user'),
]
