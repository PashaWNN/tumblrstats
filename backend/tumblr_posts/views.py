import json
from django.views import View
from backend.utils import login_required
from tumblr_posts.tasks import update_posts_and_blog_info
from tumblr_posts.services.tumblr import PostsService
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.http import HttpResponseBadRequest


class IndexView(View):
    def get(self, request):
        context = {
            'user': request.user if request.user.is_authenticated else None,
        }
        return TemplateResponse(request, 'index.html', context)


class RequestUpdateView(View):
    """
    Requests posts update for authorized user.
    User don't wait until posts is updated, it's being updated in background.
    """
    @login_required
    def get(self, request):
        blog_name = request.user.username
        interval = PostsService().check_update_interval(blog_name)
        if not interval:
            update_posts_and_blog_info.send(request.user.id)
            return HttpResponse('Update was requested.')
        else:
            return HttpResponse("Next update request is available in %d seconds" % interval, status=429)


class TopPostsView(View):
    """
    API endpoint to get top posts in JSON format
    """
    @login_required
    def get(self, request):
        count = request.GET.get('count', 5)
        blog_name = request.user.username
        if not (0 < count <= 50):
            return HttpResponseBadRequest('Count must be within 1..50')
        posts = PostsService().get_top_posts(blog_name, count=count)
        return HttpResponse(json.dumps(posts, ensure_ascii=False), content_type="application/json")


class NoteGraphView(View):
    """
    API endpoint to get statistics about notes count on all posts
    """
    @login_required
    def get(self, request):
        blog_name = request.user.username
        statistics = PostsService().get_notes_stats(blog_name)
        return HttpResponse(json.dumps(statistics), content_type="application/json")
