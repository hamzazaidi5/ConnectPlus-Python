# from django.contrib.syndication.views import Feed
# from django.utils.feedgenerator import Rss201rev2Feed
#
# from .models import Post
#
#
# class ExtendedRSSFeed(Rss201rev2Feed):
#     """
#     Create a type of RSS feed that has content:encoded elements.
#     """
#
#     def root_attributes(self) :
#         attrs = super(ExtendedRSSFeed, self).root_attributes()
#         # Because I'm adding a <content:encoded> field, I first need to declare
#         # the content namespace. For more information on how this works, check
#         # out: http://validator.w3.org/feed/docs/howto/declare_namespaces.html
#         attrs['xmlns:content'] = 'http://purl.org/rss/1.0/modules/content/'
#         return attrs
#
#     def add_item_elements(self, handler, item):
#         super(ExtendedRSSFeed, self).add_item_elements(handler, item)
#
#         # 'content_encoded' is added to the item below, in item_extra_kwargs()
#         # It's populated in item_your_custom_field(). Here we're creating
#         # the <content:encoded> element and adding it to our feed xml
#         if item['content_encoded'] is not None:
#             handler.addQuickElement(u'content_encoded', item['content_encoded'])
# class LatestPost(Feed):
#     title = 'Latest Posts'
#     link = 'posts'
#     description = 'New Post'
#     feed_type = ExtendedRSSFeed
#
#     def items(self):
#         return Post.post.all()
#
#     def item_title(self, item):
#         return item.title
#
#     def item_description(self, item):
#         return item.id
#
#     def item_link(self, item):
#         return item.get_absolute_url()
#
#     def item_extra_kwargs(self, item):
#         # return {'author': item.author, 'id': item.id}
#         extra = super(LatestPost, self).item_extra_kwargs(item)
#         # extra.update({'content_encoded': self.item_your_custom_field(item)})
#         extra[ 'content_encoded' ] = self.item_your_custom_field(item)
#         return extra
#
#     def item_your_custom_field(self, item):
#         obj_id = item.id
#         query_obj = Post.objects.get(pk = obj_id)
#         full_text = query_obj.author.username
#         return full_text
#



from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed

from .models import Post , Stream


class ExtendedRSSFeed(Rss201rev2Feed):
    """
    Create a type of RSS feed that has content:encoded elements.
    """

    def root_attributes(self) :
        attrs = super(ExtendedRSSFeed, self).root_attributes()
        # Because I'm adding a <content:encoded> field, I first need to declare
        # the content namespace. For more information on how this works, check
        # out: http://validator.w3.org/feed/docs/howto/declare_namespaces.html
        attrs['xmlns:content'] = 'http://purl.org/rss/1.0/modules/content/'
        return attrs

    def add_item_elements(self, handler, item):
        super(ExtendedRSSFeed, self).add_item_elements(handler, item)

        # 'content_encoded' is added to the item below, in item_extra_kwargs()
        # It's populated in item_your_custom_field(). Here we're creating
        # the <content:encoded> element and adding it to our feed xml
        if item['content_encoded'] is not None:
            handler.addQuickElement(u'content_encoded', item['content_encoded'])
class LatestPost(Feed):
    title = 'Latest Stream'
    link = 'posts'
    description = 'New Post'
    feed_type = ExtendedRSSFeed

    def items(self):
        return Stream.stream.all()

    def item_title(self, item):
        return item.post.title

    def item_description(self, item):
        return item.post.id

    def item_link(self, item):
        return item.post.get_absolute_url()

    def item_extra_kwargs(self, item):
        # return {'author': item.author, 'id': item.id}
        extra = super(LatestPost, self).item_extra_kwargs(item)
        # extra.update({'content_encoded': self.item_your_custom_field(item)})
        extra[ 'content_encoded' ] = self.item_your_custom_field(item)
        return extra

    def item_your_custom_field(self, item):
        obj_id = item.post.id
        query_obj = Post.objects.get(pk = obj_id)
        full_text = query_obj.author.username
        return full_text

