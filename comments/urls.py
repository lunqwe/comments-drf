from django.urls import path, include
from .views import index, AddCommentView
from rest_framework.routers import DefaultRouter



urlpatterns = [
    path('', index, name='index'),
    path('comments/create/', AddCommentView.as_view(), name='create-comment')  
]
