from django.db import models
from django.contrib.auth import get_user_model
from backend.utils import shorten_string


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Blog(models.Model):
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    blog_name = models.CharField(max_length=255)
    uuid = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    is_primary = models.BooleanField()
    avatar = models.URLField()
    followers = models.IntegerField()
    posts = models.IntegerField()
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.blog_name


class Post(models.Model):
    TYPES = [(w.capitalize(), w) for w in ('text', 'quote', 'link', 'answer', 'video', 'audio', 'photo', 'chat')]
    id = models.BigIntegerField(primary_key=True)
    blog = models.ForeignKey(to=Blog, on_delete=models.CASCADE)
    post_url = models.URLField()
    type = models.CharField(choices=TYPES, max_length=6)
    timestamp = models.IntegerField()
    date = models.DateField()
    tags = models.ManyToManyField(to=Tag)
    mobile = models.BooleanField()
    is_reblog = models.BooleanField()
    note_count = models.IntegerField()
    title = models.CharField(max_length=255, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=255, blank=True, null=True)

    def get_tags(self):
        return ', '.join([t.name for t in self.tags.all()])

    def __str__(self):
        return self.title or shorten_string(self.summary, 40) or 'Unnamed post'
