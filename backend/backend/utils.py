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
