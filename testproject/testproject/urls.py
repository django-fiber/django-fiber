from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path, re_path

from fiber.views import page

admin.autodiscover()

urlpatterns = [
    path('api/v2/', include('fiber.rest_api.urls')),
    path('admin/fiber/', include('fiber.admin_urls')),

    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('empty/', lambda request: HttpResponse('<!doctype html><html><head></head><body></body></html>')),
    re_path('', page),
]
