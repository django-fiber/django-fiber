"""
The implementation of this module is based on the example from the Django Rest Framework docs available at
http://django-rest-framework.readthedocs.org/.
"""

import os

from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse

from djangorestframework.resources import ModelResource

from fiber.models import Page, PageContentItem, ContentItem, Image, File
from fiber.utils.date import friendly_datetime
from fiber.app_settings import PERMISSION_CLASS
from fiber.utils import class_loader


from .views import ApiRoot, MovePageView, MovePageContentItemView, ListView, TreeListView, FileListView, ImageListView, InstanceView

PERMISSIONS = class_loader.load_class(PERMISSION_CLASS)


class PageResource(ModelResource):
    model = Page
    depth = 1

    def move_url(self, instance):
        """
        Provide a url on this resource that points to the
        `move_page` method on the Page model.
        """
        return reverse('page-resource-instance-move',
                       kwargs={'pk': instance.id})

    def page_url(self, instance):
        return instance.get_absolute_url()

    include = ('move_url', 'url', 'page_url')


class PageContentItemResource(ModelResource):
    model = PageContentItem
    depth = 1

    def move_url(self, instance):
        """
        Provide a url on this resource that points to the
        `move_page_content_item` method on the PageContentItem model.
        """
        return reverse('page-content-item-resource-instance-move',
                       kwargs={'pk': instance.id})

    include = ('move_url', )


class ContentItemResource(ModelResource):
    model = ContentItem
    depth = 1


class FileResource(ModelResource):
    model = File

    def file_url(self, instance):
        return instance.file.url

    def filename(self, instance):
        return os.path.basename(instance.file.name)

    def updated(self, instance):
        return friendly_datetime(instance.updated)

    def can_edit(self, instance):
        return PERMISSIONS.can_edit(self.view.user, instance)

    include = ('url', 'file_url', 'filename', 'updated', 'can_edit')


class ImageResource(FileResource):
    model = Image

    def image_url(self, instance):
        return instance.image.url

    def filename(self, instance):
        return os.path.basename(instance.image.name)

    def size(self, instance):
        return '%s x %d' % (instance.width, instance.height)

    def can_edit(self, instance):
        return PERMISSIONS.can_edit(self.view.user, instance)

    include = ('url', 'image_url', 'filename', 'size', 'updated', 'can_edit')


urlpatterns = patterns('',
    (r'^$', ApiRoot.as_view()),
    url(r'^pages/$', ListView.as_view(resource=PageResource), name='page-resource-root'),
    url(r'^pages/(?P<pk>[^/]+)/$', InstanceView.as_view(resource=PageResource), name='page-resource-instance'),
    url(r'^pages/(?P<pk>[^/]+)/move_page/$', MovePageView.as_view(), name='page-resource-instance-move'),
    url(r'^pagetree/$', TreeListView.as_view(), name='pagetree-resource'),
    url(r'^page_content_items/$', ListView.as_view(resource=PageContentItemResource), name='page-content-item-resource-root'),
    url(r'^page_content_items/(?P<pk>[^/]+)/$', InstanceView.as_view(resource=PageContentItemResource), name='page-content-item-resource-instance'),
    url(r'^page_content_items/(?P<pk>[^/]+)/move/$', MovePageContentItemView.as_view(), name='page-content-item-resource-instance-move'),
    url(r'^content_items/$', ListView.as_view(resource=ContentItemResource), name='content-item-resource-root'),
    url(r'^content_items/(?P<pk>[^/]+)/$', InstanceView.as_view(resource=ContentItemResource), name='content-item-resource-instance'),
    url(r'^images/$', ImageListView.as_view(resource=ImageResource), name='image-resource-root'),
    url(r'^images/(?P<pk>[^/]+)/$', InstanceView.as_view(resource=ImageResource), name='image-resource-instance'),
    url(r'^files/$', FileListView.as_view(resource=FileResource), name='file-resource-root'),
    url(r'^files/(?P<pk>[^/]+)/$', InstanceView.as_view(resource=FileResource), name='file-resource-instance'),
)
