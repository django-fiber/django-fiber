from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.api_root),
    url(r'^pages/$', views.PageList.as_view(), name='page-list'),
    url(r'^pages/(?P<pk>[^/]+)/$', views.PageDetail.as_view(), name='page-detail'),
    url(r'^pages/(?P<pk>[^/]+)/move_page/$', views.MovePageView.as_view(), name='page-move'),
    url(r'^pagetree/$', views.PageTree.as_view(), name='pagetree'),
    url(r'^contentitemgroups/$', views.ContentItemGroups.as_view(), name='contentitemgroups'),
    url(r'^page_content_items/$', views.PageContentItemList.as_view(), name='pagecontentitem-list'),
    url(r'^page_content_items/(?P<pk>[^/]+)/$', views.PageContentItemDetail.as_view(), name='pagecontentitem-detail'),
    url(r'^page_content_items/(?P<pk>[^/]+)/move/$', views.MovePageContentItemView.as_view(), name='pagecontentitem-move'),
    url(r'^content_items/$', views.ContentItemList.as_view(), name='contentitem-list'),
    url(r'^content_items/(?P<pk>[^/]+)/$', views.ContentItemDetail.as_view(), name='contentitem-detail'),
    url(r'^images/$', views.ImageList.as_view(), name='image-list'),
    url(r'^images/(?P<pk>[^/]+)/$', views.ImageDetail.as_view(), name='image-detail'),
    url(r'^files/$', views.FileList.as_view(), name='file-list'),
    url(r'^files/(?P<pk>[^/]+)/$', views.FileDetail.as_view(), name='file-detail'),
]
