from django.urls import path

from . import views


urlpatterns = [
    path('', views.api_root),
    path('pages/', views.PageList.as_view(), name='page-list'),
    path('pages/<int:pk>/', views.PageDetail.as_view(), name='page-detail'),
    path('pages/<int:pk>/move_page/', views.MovePageView.as_view(), name='page-move'),
    path('pagetree/', views.PageTree.as_view(), name='pagetree'),
    path('contentitemgroups/', views.ContentItemGroups.as_view(), name='contentitemgroups'),
    path('page_content_items/', views.PageContentItemList.as_view(), name='pagecontentitem-list'),
    path('page_content_items/<int:pk>/', views.PageContentItemDetail.as_view(), name='pagecontentitem-detail'),
    path('page_content_items/<int:pk>/move/', views.MovePageContentItemView.as_view(), name='pagecontentitem-move'),
    path('content_items/', views.ContentItemList.as_view(), name='contentitem-list'),
    path('content_items/<int:pk>/', views.ContentItemDetail.as_view(), name='contentitem-detail'),
    path('images/', views.ImageList.as_view(), name='image-list'),
    path('images/<int:pk>/', views.ImageDetail.as_view(), name='image-detail'),
    path('files/', views.FileList.as_view(), name='file-list'),
    path('files/<int:pk>/', views.FileDetail.as_view(), name='file-detail'),
]
