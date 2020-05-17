from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('oauth/', include('tumblr_auth.urls')),
    path('api/', include('tumblr_posts.urls')),
]

