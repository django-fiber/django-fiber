from django.conf.urls import include, url
from django.views.i18n import javascript_catalog

from . import admin_views
from . import fiber_admin


urlpatterns = [
    url(r'^page/(?P<id>\d+)/move_up/$', admin_views.page_move_up, name='fiber_page_move_up'),
    url(r'^page/(?P<id>\d+)/move_down/$', admin_views.page_move_down, name='fiber_page_move_down'),
    url(r'^login/$', admin_views.fiber_login, name='fiber_login'),
    url(r'^pages.json$', admin_views.pages_json, name='pages_json'),
    url(r'^fiber_admin/', include(fiber_admin.site.urls)),
    url(r'^jsi18n/$', javascript_catalog, {'packages': ['fiber']}, name='fiber_i18n'),
]
