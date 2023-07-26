from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views
from .feeds import LatestPost

urlpatterns = [
    path("", views.PostList.as_view(), name= 'posts'),
    path("stream/<int:pk>", views.StreamList.as_view(), name= 'stream'),
    path('login/', views.CustomLoginView.as_view(), name = 'login'),
    path('logout/', LogoutView.as_view(next_page = 'login'), name = 'logout'),
    path('register/', views.RegisterPage.as_view(), name = 'register'),
    path('post/<int:pk>/', views.PostDetail.as_view() , name = 'post'),
    path('create-post/', views.PostCreate.as_view(), name='post-create'),
    path('update-post/<int:pk>/', views.PostUpdate.as_view(), name='post-update'),
    path('feed/', LatestPost(), name='feed'),
    path('follow/<int:pk>/', views.follow, name='follow'),
    path('user/<int:pk>/', views.UserDetail.as_view(), name = 'user'),

]