from functools import wraps

from django.http import HttpResponse


def shorten_string(string, length=100):
    if len(string) <= length:
        return string
    else:
        return string[:length] + '...'


def login_required(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponse("You must be logged in", status=401)
        return func(self, request, *args, **kwargs)
    return wrapper