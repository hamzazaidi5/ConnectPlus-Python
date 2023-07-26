from django.contrib import admin

from .models import Post, Follow, Stream


#
# @admin.register(UserApp)
# class UserAppAdminModel(admin.ModelAdmin):
#     pass


@admin.register(Post)
class PostAdminModel(admin.ModelAdmin):
    pass


@admin.register(Follow)
class FollowAdminModel(admin.ModelAdmin):
    pass


@admin.register(Stream)
class StreamAdminModel(admin.ModelAdmin):
    pass
