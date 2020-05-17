from tumblr_posts import views
from django.urls import path

urlpatterns = [
    path('', views.IndexView.as_view()),
    path('request_update/', views.RequestUpdateView.as_view()),
    path('top/', views.TopPostsView.as_view()),
    path('note_graph/', views.NoteGraphView.as_view()),
]
