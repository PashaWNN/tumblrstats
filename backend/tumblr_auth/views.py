import json
from backend.utils import login_required
from tumblr_posts.tasks import update_posts_and_blog_info
from django.views import View
from tumblr_auth.services.auth import AuthService
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, HttpResponse


class LoginView(View):
    def get(self, request):
        if isinstance(request.user, AnonymousUser):
            auth_service = AuthService()
            uri = auth_service.get_login_uri(request)
            return HttpResponseRedirect(uri)
        else:
            return HttpResponseRedirect('/')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/')


class CallbackView(View):
    def get(self, request):
        auth_service = AuthService()
        token = request.session.get('tumblr_request_token')
        secret = request.session.get('tumblr_request_secret')
        verifier = request.GET.get('oauth_verifier')
        info = auth_service.login_user(request, token, secret, verifier)
        if info and info.get('created', False):
            update_posts_and_blog_info.send(request.user.id)
        return HttpResponseRedirect('/')


class UserInfoView(View):
    @login_required
    def get(self, request):
        info = AuthService().get_user_info(request.user)
        return HttpResponse(json.dumps(info, ensure_ascii=False), content_type="application/json")
