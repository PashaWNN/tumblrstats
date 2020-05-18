import dramatiq
from django.contrib.auth import get_user_model
from dramatiq.rate_limits.backends import RedisBackend
from dramatiq.rate_limits import ConcurrentRateLimiter
from tumblr_posts.services.tumblr import PostsService, BlogsService


@dramatiq.actor()
def update_posts_and_blog_info(user_id: int):
    """
    Task for asynchronous updating posts and blog information

    :param user_id: user id in django
    """
    user = get_user_model().objects.get(id=user_id)
    blog_name = user.username
    mutex = ConcurrentRateLimiter(RedisBackend(), f"mutex-blog-{blog_name}", limit=1)
    with mutex.acquire(raise_on_failure=False) as acquired:
        if not acquired:
            return False
        BlogsService().update_user_info(user)
        PostsService().update_posts(blog_name)