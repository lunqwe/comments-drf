from django.urls import path, include
from .views import index, AddCommentView, CommentListView
from rest_framework.routers import DefaultRouter



urlpatterns = [
    path('', index, name='index'),
    path('create/', AddCommentView.as_view(), name='create-comment'),
    path('get/', CommentListView.as_view(), name='comment-list'), 
]
