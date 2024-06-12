from django.db import models
from config import settings

class Comment(models.Model):
    created_by_username = models.CharField('Created by (Username)', max_length=255, default='Guest')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    email = models.EmailField('Email', default='')
    text = models.TextField('Text')
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='files/', blank=True, null=True)
    home_page = models.URLField(blank=True, null=True)
    to_comment = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)