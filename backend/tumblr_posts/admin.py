from django.contrib import admin
from tumblr_posts import models


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'title', 'summary', 'get_tags', 'date', 'is_reblog')
    list_filter = ('is_reblog', 'mobile', 'blog', 'tags')
    sortable_by = ('note_count', 'date', 'timestamp')


@admin.register(models.Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('blog_name', 'title', 'user', 'followers', 'posts', 'updated')
