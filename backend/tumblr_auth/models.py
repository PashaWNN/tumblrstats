from django.db import models
from django.contrib.auth import get_user_model


class TumblrCredentials(models.Model):
    user = models.OneToOneField(to=get_user_model(), on_delete=models.CASCADE)
    token = models.CharField(max_length=255, editable=False)
    secret = models.CharField(max_length=255, editable=False)