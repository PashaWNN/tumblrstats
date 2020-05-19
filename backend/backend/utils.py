import re
from functools import wraps

from django.http import HttpResponse


def shorten_string(string: str, length=100) -> str:
    """
    Shorten string if needed and append ellipsis at the end

    :param string: original string
    :param length: maximum length
    :return: shortened string
    """
    if len(string) <= length:
        return string
    else:
        return string[:length] + '...'


def login_required(func):
    """
    Decorator for views to check authorization. Will return 401 error if user is not authenticated
    """
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponse("You must be logged in", status=401)
        return func(self, request, *args, **kwargs)
    return wrapper


def shorten_post_url(url):
    """
    Function for removing slug from post url

    :param url: original url in format https://blog-name.tumblr.com/post/id/slug
    :return: shortened url without slug or original url if can't match it
    """
    match = re.match(r'http(?:s)://.+tumblr\.com/post/[0-9]+/', url)
    if match is not None:
        return match.group(0)
    else:
        return url