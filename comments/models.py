from django.db import models
from config import settings

class Comment(models.Model):
    created_by_username = models.CharField("Created by (Username)", max_length=255, default='Guest')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    email = models.EmailField('Email', default='')
    text = models.TextField('Text')
    created_at = models.DateTimeField(auto_now_add=True)