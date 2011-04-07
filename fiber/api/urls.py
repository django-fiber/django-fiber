from django.conf.urls.defaults import *

from piston.resource import Resource

from authentication import DjangoStaffAuthentication, DjangoUploadAuthentication
from handlers import PageHandler, PageContentItemHandler, ImageHandler, FileHandler, FileUploadHandler, ImageUploadHandler, ContentItemHandler
from emitters import jqGridJSONEmitter

auth = DjangoStaffAuthentication()
upload_auth = DjangoUploadAuthentication()

page_handler = Resource(PageHandler, authentication=auth)
page_content_item_handler = Resource(PageContentItemHandler, authentication=auth)
image_handler = Resource(ImageHandler, authentication=auth)
file_handler = Resource(FileHandler, authentication=auth)
file_upload_handler = Resource(FileUploadHandler, authentication=upload_auth)
image_upload_handler = Resource(ImageUploadHandler, authentication=upload_auth)
content_item_handler = Resource(ContentItemHandler, authentication=auth)

urlpatterns = patterns('',
    url(r'^pages/$', page_handler),
    url(r'^pages\.(?P<emitter_format>.+)$', page_handler),
    url(r'^page/(?P<id>\d+)/$', page_handler),
    url(r'^page_content_items/$', page_content_item_handler),
    url(r'^page_content_items\.(?P<emitter_format>.+)$', page_content_item_handler),
    url(r'^page_content_item/(?P<id>\d+)/$', page_content_item_handler),
    url(r'^images\.(?P<emitter_format>.+)$', image_handler),
    url(r'^files\.(?P<emitter_format>.+)$', file_handler),
    url(r'^files/$', file_upload_handler),
    url(r'^images/$', image_upload_handler),
    url(r'^content_item/(?P<id>\d+)/$', content_item_handler),
)
