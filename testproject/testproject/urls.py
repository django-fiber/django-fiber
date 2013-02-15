try:
    # Django >= 1.4
    from django.conf.urls import patterns, include
except ImportError:
    # Django 1.3
    from django.conf.urls.defaults import patterns, include

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    (r'^api/v2/', include('fiber.rest_api.urls')),
    (r'^admin/fiber/', include('fiber.admin_urls')),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {'packages': ('fiber',), }),

    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += patterns('',
    (r'', 'fiber.views.page'),
)
