import pytumblr
import requests
from django.conf import settings
from django.contrib.auth import get_user_model, login
from requests_oauthlib import OAuth1
from tumblr_auth.models import TumblrCredentials
from tumblr_auth.exceptions import UnauthorizedError


def parse_qs(query_string):
    result = {}
    for pair in query_string.split('&'):
        key, value = pair.split('=')
        result[key] = value
    return result


def _parse_avatar(avatars_info, resolution):
    avatar_info_list = [a for a in avatars_info if a['width'] == resolution]
    if avatar_info_list:
        avatar_info = avatar_info_list[0]
        return avatar_info.get('url')


def _parse_blog_info(blog):
    return {
        'name': blog['name'],
        'uuid': blog['uuid'],
        'title': blog['title'],
        'avatar': _parse_avatar(blog['avatar'], 128),
        'is_primary': blog['primary'],
        'posts': blog['posts'],
        'followers': blog['followers'],
    }


class AuthService:
    def __init__(self):
        self.user_model = get_user_model()

    @staticmethod
    def get_tumblr_client(token, secret):
        return pytumblr.TumblrRestClient(
            consumer_key=settings.TUMBLR_CONSUMER_KEY,
            consumer_secret=settings.TUMBLR_CONSUMER_SECRET,
            oauth_token=token,
            oauth_secret=secret,
        )

    @staticmethod
    def get_session_key(request):
        if request.session.session_key is None:
            request.session.save()
        return request.session.session_key

    def get_login_uri(self, request):
        oauth = OAuth1(client_key=settings.TUMBLR_CONSUMER_KEY, client_secret=settings.TUMBLR_CONSUMER_SECRET)
        response = requests.post(settings.TUMBLR_REQUEST_TOKEN_URL, auth=oauth)
        payload = parse_qs(response.text)
        token = payload['oauth_token']
        secret = payload['oauth_token_secret']
        request.session['tumblr_request_token'] = token
        request.session['tumblr_request_secret'] = secret
        return settings.TUMBLR_AUTHORIZATION_URL + '?oauth_token=' + token

    def login_user(self, request, token, secret, verifier):

        oauth = OAuth1(client_key=settings.TUMBLR_CONSUMER_KEY, client_secret=settings.TUMBLR_CONSUMER_SECRET,
                       resource_owner_key=token, resource_owner_secret=secret, verifier=verifier)
        r = requests.post(settings.TUMBLR_ACCESS_TOKEN_URL, auth=oauth)
        if r.status_code == 200:
            payload = parse_qs(r.text)
            access_token = payload['oauth_token']
            access_token_secret = payload['oauth_token_secret']
            client = self.get_tumblr_client(access_token, access_token_secret)
            info = client.info()
            if info is not None:
                user, created = self.user_model.objects.get_or_create(username=info['user']['name'])
                TumblrCredentials.objects.update_or_create(user=user, defaults={
                    'token': access_token,
                    'secret': access_token_secret,
                })
                info['created'] = created
                login(request, user)
            return info

    def get_user_info(self, user):
        if not user.tumblrcredentials:
            raise UnauthorizedError()
        token, secret = user.tumblrcredentials.token, user.tumblrcredentials.secret
        client = self.get_tumblr_client(token, secret)
        info = client.info()['user']
        result = {
            'name': info['name'],
            'likes': info['likes'],
            'following': info['following'],
            'blogs': [_parse_blog_info(blog) for blog in info['blogs']],
        }
        return result
