from typing import List, Optional
from django.conf import settings
from django.contrib.auth import get_user_model
from tumblr_posts.models import Post, Tag, Blog
from tumblr_auth.services.auth import AuthService
import pytumblr
import datetime
from redis import Redis


user_model = get_user_model()


class LimitError(RuntimeError):
    pass


class PostsService:
    """
    Posts service which is responsible for getting information about posts
    """
    def __init__(self):
        self.api_key = settings.TUMBLR_CONSUMER_KEY
        self.client = pytumblr.TumblrRestClient(self.api_key)
        self.interval = settings.MIN_POSTS_UPDATE_INTERVAL
        self.redis = Redis(**settings.REDIS)
        self.interval_key = '{}-updated'

    def _retrieve_posts(self, blog_name) -> list:
        """
        Get all posts from blog by it's name

        :param blog_name: blog name
        :return: list of posts
        """
        posts = []
        offset = 0
        limit = 50
        while True:
            payload = self.client.posts(blog_name, limit=limit, offset=offset, reblog_info=True)
            posts += payload['posts']
            if not payload['posts']:
                break
            offset += limit
        return posts

    def check_update_interval(self, blog_name):
        """
        Check whether posts update is available (i.e. not bumped to limit)

        :param blog_name: blog name to check
        :return: seconds to next available update or None if can update now
        """
        ttl = self.redis.ttl(self.interval_key.format(blog_name))
        return ttl if ttl > 0 else None

    def update_posts(self, user: user_model, blog_name: Optional[str] = None) -> None:
        """
        Update posts for specific blog

        :param user: User object
        :param blog_name: blog name
        """
        self.redis.set(self.interval_key.format(blog_name), 1, ex=self.interval)
        blog = BlogsService().get_user_blog(user, blog_name)
        posts = self._retrieve_posts(blog_name)

        for post in posts:
            tags = []
            for tag in post['tags']:
                tag_object, created = Tag.objects.get_or_create(name=tag)
                tags.append(tag_object)
            post_object, created = Post.objects.update_or_create(
                id=post['id'],
                defaults={
                    'blog': blog,
                    'post_url': post['post_url'],
                    'date': datetime.datetime.strptime(post['date'], '%Y-%m-%d %H:%M:%S GMT'),
                    'is_reblog': 'reblogged_from_id' in post,
                    'summary': post['summary'] or '',
                    'slug': post['slug'] or '',
                    'note_count': post['note_count'],
                    'title': post.get('title') or '',
                    'timestamp': post['timestamp'],
                    'mobile': post.get('mobile', False),
                }
            )
            post_object.tags.set(tags)

    def get_top_posts(self, user: user_model, blog_name: Optional[str] = None, count=5, exclude_reblogs=True) -> list:
        """
        Get posts top for specific blog

        :param user: User object
        :param blog_name: blog name
        :param count: count of posts to get, defaults to 5
        :param exclude_reblogs: exclude reblogs (useful because reblogged posts often have too much likes)
        :return: posts top list
        """
        blog = BlogsService().get_user_blog(user, blog_name)
        posts = Post.objects.filter(blog=blog).order_by('-note_count')
        if exclude_reblogs:
            posts = posts.filter(is_reblog=False)
        result = []
        for post in posts[:count]:
            result.append({
                'title': str(post),
                'note_count': post.note_count,
                'url': post.post_url,
            })
        return result

    def get_notes_stats(self, user: user_model, blog_name: Optional[str] = None, exclude_reblogs=True) -> List[int]:
        """
        Get just notes counts on all posts. Useful for drawing a graph of notes per post

        :param user: User object
        :param blog_name: blog name
        :param exclude_reblogs: exclude reblogs (useful because reblogged posts often have too much likes)
        :return:
        """
        blog = BlogsService.get_user_blog(user, blog_name)
        posts = Post.objects.filter(blog=blog).order_by('timestamp').values_list('note_count', flat=True)
        if exclude_reblogs:
            posts.filter(is_reblog=False)
        return [i for i in posts]


class BlogsService:
    """
    Blogs service which is responsible for getting info about Tumblr blogs
    """
    def __init__(self):
        self.api_key = settings.TUMBLR_CONSUMER_KEY
        self.client = pytumblr.TumblrRestClient(self.api_key)
        self.interval = settings.MIN_POSTS_UPDATE_INTERVAL
        self.redis = Redis(**settings.REDIS)
        self.interval_key = '{}-updated'

    def get_user_blog(self, user: user_model, blog_name: Optional[str] = None) -> dict:
        """
        Get blog by it's name. This method should be used everywhere instead of getting directly
        from database, as this method automatically gets blogs info from tumblr if it's not present
        in database yet

        :param blog_name: blog name or None if primary blog needed
        :return: Blog object
        """
        if blog_name is None:
            blog_name = user.username
        try:
            blog = Blog.objects.get(blog_name=blog_name)
        except Blog.DoesNotExist:
            self.update_user_info(user)
            blog = Blog.objects.get(blog_name=blog_name)
        return blog


    def update_user_info(self, user: user_model) -> None:
        """
        Update user info from Tumblr

        :param user: User object
        """
        blog_name = user.username
        self.redis.set(self.interval_key.format(blog_name), 1, ex=self.interval)
        info = AuthService().get_user_info(user)
        primary_blog = None
        for blog in info['blogs']:
            Blog.objects.update_or_create(
                uuid=blog['uuid'],
                defaults=dict(
                    blog_name=blog['name'],
                    title=blog['title'],
                    user=user,
                    avatar=blog['avatar'],
                    is_primary=blog['is_primary'],
                    posts=blog['posts'],
                    followers=blog['followers'],
                ),
            )
            if blog['is_primary']:
                primary_blog = blog
        user.username = primary_blog['name']
        user.save()
