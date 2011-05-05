from django.conf.urls.defaults import *

from admin_views import *
from admin import fiber_admin_site


urlpatterns = patterns('',
    url(r'^page/(?P<id>\d+)/move_up/$', page_move_up, name='fiber_page_move_up'),
    url(r'^page/(?P<id>\d+)/move_down/$', page_move_down, name='fiber_page_move_down'),
    url(r'^login/$', fiber_login, name='fiber_login'),
    (r'^fiber_admin/', include(fiber_admin_site.urls)),
)
