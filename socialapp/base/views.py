import csv
import pandas as pd
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

def bulk_create_singleCSV(self, file):
    csvreader = csv.reader(file.read().decode('utf-8').splitlines())
    next(csvreader)
    rows = []
    for row in csvreader:
        rows.append(row)

    objects = [Post(title = row[0], description = row[1], author = self.request.user) for row in rows]
    print(objects)
    Post.objects.bulk_create(objects)

def bulk_update_singleCSV(self, file):
    csvreader = csv.reader(file.read().decode('utf-8').splitlines())
    next(csvreader)
    rows = []
    for row in csvreader:
        rows.append(row)

    updates = [{'title': row[0], 'description': row[1]} for row in rows]

    posts = Post.objects.filter(author = self.request.user)

    updated_posts = []
    for post in posts:
        for update in updates:
            if post.title == update['title']:
                post.description = update['description']
                updated_posts.append(post)

    print("Updated", updated_posts)

    updated_ones = Post.objects.bulk_update(updated_posts, ['description'])
    print(updated_ones)


def bulk_create_multiple_file(self, file):
    data = pd.read_excel(file, sheet_name = None)
    objects = []
    for sheet_name, sheet_data in data.items():
        for index, row in sheet_data.iterrows():
            post = Post(title = row['title'], description = row['description'], author = self.request.user)
            objects.append(post)
    print(objects)
    Post.objects.bulk_create(objects)

def bulk_update_multiple_file(self, file):
    data = pd.read_excel(file, sheet_name= None)
    objects = []
    for sheet_name, sheet_data in data.items():
        for index, row in sheet_data.iterrows():
            post = Post(title = row['title'], description = row['description'], author = self.request.user)
            objects.append(post)
    #print(objects)

    filtered_posts = Post.objects.filter(author = self.request.user)
    #print(list(filtered_posts))

    updated_posts = []
    for post in filtered_posts:
        for obj in objects:
            if post.title == obj.title:
                post.description = obj.description
                updated_posts.append(post)

    updated_ones = Post.objects.bulk_update(updated_posts, ['description'])
    print(updated_ones)

class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'author']
    success_url = reverse_lazy("posts")
    template_name = "templates/base/post_update.html"

    def form_valid(self, form):
        file = self.request.FILES.get("file")
        bulk_update_multiple_file(self, file)
        form.save()
        return super().form_valid(form)

class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    fields = ["title", "description"]
    success_url = reverse_lazy("posts")
    template_name = "templates/base/post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.file = self.request.FILES.get("file")
        file = form.instance.file

        #bulk_create_singleCSV(self, file)
        bulk_create_multiple_file(self, file)

        form.save()
        return super(CreateView, self).form_valid(form)

def follow(request, pk):
    user = User.objects.get(id=pk)
    if request.method == "POST" or "GET":
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
    return reverse("posts")
