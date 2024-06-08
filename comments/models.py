from django.db import models


class Comment(models.Model):
    created_by = models.CharField("Username", max_length=255, default='Guest')
    email = models.EmailField('Email', default='')
    text = models.TextField('Text')
    created_at = models.DateTimeField(auto_now_add=True)