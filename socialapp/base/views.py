from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
import requests
from django.http import HttpResponse , HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, ListView, DetailView, CreateView, UpdateView

from .models import Post, Follow, Stream
from bs4 import BeautifulSoup


class CustomLoginView(LoginView):
    template_name = "templates/base/login.html"
    fields = "__all__"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("posts")


class RegisterPage(FormView):
    template_name = "templates/base/register.html"
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy("posts")

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)


def index(request):
    return render(request, "templates/base/main.html")


class PostList(LoginRequiredMixin, ListView):
    model = Post
    context_object_name = "posts"
    template_name = "templates/base/post_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        context["posts"] = Post.objects.filter(author=current_user)
        users = User.objects.all()
        current_user = self.request.user
        context["users"] = [user for user in users if user != current_user]
        context["current_user"] = self.request.user.id
        return context


class StreamList(LoginRequiredMixin, ListView):
    model = Stream
    template_name = "templates/base/stream_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        url = requests.get("http://localhost:8000/feed/")
        soup = BeautifulSoup(url.content, "lxml")
        posts = soup.find_all("item")
        values = []
        for post in posts:
            entry = {
                "title": post.title.text,
                "link": post.guid.text,
                "description": post.description.text,
                "author": post.content_encoded.text,
            }
            values.append(entry)

        context["posts"] = values
        return context


class PostDetail(LoginRequiredMixin, DetailView):
    model = Post


class UserDetail(LoginRequiredMixin, DetailView):
    model = User
    template_name = "templates/base/user_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        print("User ", user)
        context["posts"] = Post.objects.filter(author=user)
        context["user"] = user
        print(context["user"], context["posts"])
        user_obj = User.objects.filter(username=user).first()

        filter_follow = Follow.objects.filter(following=user_obj)
        # print("filter", filter_follow.first().following)
        context["follow"] = filter_follow
        if Follow.objects.filter(following=user_obj).exists():
            if self.request.user == filter_follow.first().follower:
                context["check"] = True
                print("True condition check", context["check"])
            else:
                context["check"] = False
                print("False condition check", context["check"])
        else:
            context["check"] = False
        context["user_id"] = user_obj.pk
        return context


class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    fields = ["title", "description"]
    success_url = reverse_lazy("posts")
    template_name = "templates/base/post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(CreateView, self).form_valid(form)


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ["title", "description"]
    success_url = reverse_lazy("posts")
    template_name = "templates/base/post_form.html"


def follow(request, pk):
    user = User.objects.get(id=pk)
    if request.method == "POST" or "GET":
        if request.user not in user.following.all():
            if Follow.objects.filter(follower=request.user, following=user).exists():
                Follow.objects.filter(follower=request.user, following=user).delete()
                print(f"{request.user} unfollowed {user}! ")
                return redirect(f"/user/{pk}")
            else:
                follow_obj = Follow.objects.create(
                    follower=request.user, following=user
                )
                follow_obj.save()
                print(f"{request.user} followed {user} successfully!")
                return redirect(f"/user/{pk}")
        elif request.user in user.following.all():
            return HttpResponse("In elif")
    return reverse("posts")
