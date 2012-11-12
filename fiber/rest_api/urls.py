"""
The implementation of this module is based on the example from the Django Rest Framework docs available at
http://django-rest-framework.readthedocs.org/.
"""

from django.conf.urls.defaults import patterns, url

from .views import MovePageView, MovePageContentItemView, TreeListView

from .views import api_root, PageList, PageDetail, PageContentItemList, PageContentItemDetail, ContentItemList, ContentItemDetail, ImageList, ImageDetail, FileList, FileDetail


urlpatterns = patterns('',
    (r'^$', api_root),
    url(r'^pages/$', PageList.as_view(), name='page-list'),
    url(r'^pages/(?P<pk>[^/]+)/$', PageDetail.as_view(), name='page-detail'),
    url(r'^pages/(?P<pk>[^/]+)/move_page/$', MovePageView.as_view(), name='page-resource-instance-move'),
    url(r'^pagetree/$', TreeListView.as_view(), name='pagetree-resource'),
    url(r'^page_content_items/$', PageContentItemList.as_view(), name='pagecontentitem-list'),
    url(r'^page_content_items/(?P<pk>[^/]+)/$', PageContentItemDetail.as_view(), name='pagecontentitem-detail'),
    url(r'^page_content_items/(?P<pk>[^/]+)/move/$', MovePageContentItemView.as_view(), name='page-content-item-resource-instance-move'),
    url(r'^content_items/$', ContentItemList.as_view(), name='contentitem-list'),
    url(r'^content_items/(?P<pk>[^/]+)/$', ContentItemDetail.as_view(), name='contentitem-detail'),
    url(r'^images/$', ImageList.as_view(), name='image-list'),
    url(r'^images/(?P<pk>[^/]+)/$', ImageDetail.as_view(), name='image-detail'),
    url(r'^files/$', FileList.as_view(), name='file-list'),
    url(r'^files/(?P<pk>[^/]+)/$', FileDetail.as_view(), name='file-detail'),
)
