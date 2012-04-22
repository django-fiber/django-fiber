"""
The implementation of this module is based on the example from the Django Rest Framework docs available at 
http://django-rest-framework.readthedocs.org/.
"""

from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse

from djangorestframework.resources import ModelResource

from fiber.models import Page, PageContentItem, ContentItem, Image, File


from views import ApiRoot, MovePageView, PageListView, PageInstanceView


class PageResource(ModelResource):
    model = Page

    def move_url(self, instance):
        """
        Provide a url on this resourece that points to the 
        `move_page` method on the Page model.
        """
        return reverse('page-resource-instance-move',
                       kwargs={'pk': instance.id})

    include = ('move_url', )

class PageContentItemResource(ModelResource):
    model = PageContentItem

class ContentItemResource(ModelResource):
    model = ContentItem

class ImageResource(ModelResource):
    model = Image

class FileResource(ModelResource):
    model = File


urlpatterns = patterns('',
    (r'^$', ApiRoot.as_view()),
    url(r'^pages/$', PageListView.as_view(resource=PageResource), name='page-resource-root'),
    url(r'^pages/(?P<pk>[^/]+)/$', PageInstanceView.as_view(resource=PageResource), name='page-resource-instance'),
    url(r'^pages/(?P<pk>[^/]+)/move_page/$', MovePageView.as_view(), name='page-resource-instance-move'),
    url(r'^page_content_items/$', PageListView.as_view(resource=PageContentItemResource), name='page-content-item-resource-root'),
    url(r'^page_content_items/(?P<pk>[^/]+)/$', PageInstanceView.as_view(resource=PageContentItemResource), name='page-content-item-resource-instance'),
    url(r'^content_items/$', PageListView.as_view(resource=ContentItemResource), name='content-item-resource-root'),
    url(r'^content_items/(?P<pk>[^/]+)/$', PageInstanceView.as_view(resource=ContentItemResource), name='content-item-resource-instance'),
    url(r'^images/$', PageListView.as_view(resource=ImageResource), name='image-resource-root'),
    url(r'^images/(?P<pk>[^/]+)/$', PageInstanceView.as_view(resource=ImageResource), name='image-resource-instance'),
    url(r'^files/$', PageListView.as_view(resource=FileResource), name='file-resource-root'),
    url(r'^files/(?P<pk>[^/]+)/$', PageInstanceView.as_view(resource=FileResource), name='file-resource-instance'),
)