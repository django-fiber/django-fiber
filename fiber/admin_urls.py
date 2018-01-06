from django.conf.urls import url
from django.views.i18n import JavaScriptCatalog

from . import admin_views
from . import fiber_admin

urlpatterns = [
    url(r'^page/(?P<id>\d+)/move_up/$', admin_views.page_move_up, name='fiber_page_move_up'),
    url(r'^page/(?P<id>\d+)/move_down/$', admin_views.page_move_down, name='fiber_page_move_down'),
    url(r'^login/$', admin_views.fiber_login, name='fiber_login'),
    url(r'^pages.json$', admin_views.pages_json, name='pages_json'),
    url(r'^fiber_admin/', fiber_admin.site.urls),
    url(r'^jsi18n/$', JavaScriptCatalog.as_view(), {'packages': 'fiber'}, name='fiber_i18n'),
]
