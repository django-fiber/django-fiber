from django.conf.urls.defaults import *

import fiber_admin
import admin_views


urlpatterns = patterns('',
    url(r'^page/(?P<id>\d+)/move_up/$', admin_views.page_move_up, name='fiber_page_move_up'),
    url(r'^page/(?P<id>\d+)/move_down/$', admin_views.page_move_down, name='fiber_page_move_down'),
    url(r'^login/$', admin_views.fiber_login, name='fiber_login'),
    url(r'^pages.json$', admin_views.pages_json, name='pages_json'),
    (r'^fiber_admin/', include(fiber_admin.site.urls)),
)
