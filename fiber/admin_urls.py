from django.urls import path
from django.views.i18n import JavaScriptCatalog

from . import admin_views
from . import fiber_admin

urlpatterns = [
    path('page/<int:id>/move_up/', admin_views.page_move_up, name='fiber_page_move_up'),
    path('page/<int:id>/move_down/', admin_views.page_move_down, name='fiber_page_move_down'),
    path('login/', admin_views.fiber_login, name='fiber_login'),
    path('pages.json', admin_views.pages_json, name='pages_json'),
    path('fiber_admin/', fiber_admin.site.urls),
    path('jsi18n/', JavaScriptCatalog.as_view(), {'packages': 'fiber'}, name='fiber_i18n'),
]
