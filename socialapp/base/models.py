from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count , Q
from django.db.models.signals import post_save , post_delete , pre_delete
from django.dispatch import receiver
from django.urls import reverse
from django.contrib.auth import get_user

from .managers import PostManager

class Post(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    post = PostManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post', kwargs={"pk": self.pk})


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    date = models.DateTimeField(auto_now_add = True)


    def __str__(self):
        return str(self.pk)


@receiver(post_save, sender=Post)
def create_follow_after_post_created(sender, instance, created, **kwargs):
    if created:
        author_created = instance.author
        print(author_created)
        if Follow.objects.filter(follower = author_created).exists():
            check_following = Follow.objects.filter(follower = author_created)
            print(check_following.first().following)
            new_follow = Follow.objects.create(follower = author_created, following = check_following.first().following)
            new_follow.save()
        elif Follow.objects.filter(following = author_created).exists():
            check_following = Follow.objects.filter(following = author_created)
            new_follow = Follow.objects.create(follower = check_following.first().follower,
                                               following = author_created)
            new_follow.save()
        else:
            return

@receiver(pre_delete, sender = Follow)
def delete_stream_after_delete_follow(sender, instance, **kwargs):

    user_follower = instance.follower
    user_following = instance.following
    user_follower_posts = Post.objects.filter(author = user_follower)
    user_following_posts = Post.objects.filter(author = user_following)

    for i in range(0, len(user_follower_posts)):
        get_obj = Stream.objects.filter(following = instance.following, user = instance.follower, post = user_follower_posts[i])
        get_obj.delete()

    for i in range(0, len(user_following_posts)):
        get_newobj = Stream.objects.filter(following = instance.follower, user = instance.following, post = user_following_posts[i])
        get_newobj.delete()

    # current_user_posts = Post.objects.filter(author = user_follower)
    # for i in range(0, len(current_user_posts)):
    #     stream_obj = Stream.objects.create(user = instance.follower, post = current_user_posts[i])
    #     stream_obj.save()


@receiver(post_save, sender=Follow)
def create_stream(sender, instance, created, **kwargs):
    if created:
        user_follower = instance.follower
        user_following = instance.following
        user_follower_posts = Post.objects.filter(author = user_follower)
        user_following_posts = Post.objects.filter(author = user_following)

        for i in range(0,len(user_follower_posts)):
            user_stream = Stream.objects.create(
                following=instance.following,
                user=instance.follower,
                post=user_follower_posts[i],
            )
            user_stream.save()

        for i in range(0,len(user_following_posts)):
            follower_stream = Stream.objects.create(
                following=instance.follower,
                user=instance.following,
                post=user_following_posts[i],
            )
            follower_stream.save()


class StreamManager(models.Manager):

    def get_queryset(self):
        # follows = Follow.objects.filter(follower = 1).values_list('following', flat = True)
        # print(follows)
        # return super().get_queryset().filter(following__in = follows).order_by('-date')
        return super().get_queryset().order_by('-date')
        # return super().get_queryset().filter(following__in = user)


class Stream(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stream_following')
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "stream_user")
    post = models.ForeignKey(Post, on_delete = models.CASCADE, null = True)
    date = models.DateTimeField(auto_now_add = True)
    stream = StreamManager()
    objects = models.Manager()

    def __str__(self):
        return str(self.pk)


@receiver(post_save, sender=Stream)
def delete_duplicate_streams(sender, instance, **kwargs):
    duplicates = Stream.objects.filter(following = instance.following, user = instance.user,
                                       post = instance.post)
    if duplicates.count() > 1:
        keep_object = duplicates.first()
        duplicates.exclude(pk = keep_object.pk).delete()
        print(keep_object)

