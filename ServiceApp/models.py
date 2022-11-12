from django.db import models


class Note(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    destroyTime = models.DateTimeField(null=True)
    isDestroyed = models.BooleanField(default=False)
    hasPassword = models.BooleanField(default=False)
    askForConfirmation = models.BooleanField(default=False)
    message = models.TextField(blank=False)
    frontendSecretKey = models.CharField(max_length=255, blank=False)
    backendSecretKey = models.CharField(max_length=255, blank=False)
    url = models.CharField(max_length=255, blank=False, default='')
    password = models.CharField(max_length=255, blank=True, default='')
    confirmPassword = models.CharField(max_length=255, blank=True, default='')
    name = models.CharField(max_length=255, blank=True, default='')
    email = models.EmailField(blank=True, unique=True,null=True)

    class Meta:
        ordering = ['createdAt']
