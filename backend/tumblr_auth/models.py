from django.db import models
from django.contrib.auth import get_user_model


class TumblrCredentials(models.Model):
    """
    Additional model linked to User model to store credentials for accessing Tumblr
    on behalf of specific users
    """
    user = models.OneToOneField(to=get_user_model(), on_delete=models.CASCADE)
    token = models.CharField(max_length=255, editable=False)
    secret = models.CharField(max_length=255, editable=False)