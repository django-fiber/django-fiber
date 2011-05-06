import os
from fiber.models import Image
from piston.handler import BaseHandler
from fiber.utils.date import friendly_datetime


class ImageHandler(BaseHandler):
    allowed_methods = ('GET', )
    fields = ('id', 'url', 'image', 'filename', 'size', 'updated')
    exclude = () # un-exclude `id`
    model = Image

    @classmethod
    def url(cls, image):
        return image.image.url

    @classmethod
    def image(cls, image):
        return image.image.url

    @classmethod
    def filename(cls, image):
        return os.path.basename(image.image.name)

    @classmethod
    def size(cls, image):
        return '%s x %d' % (image.width, image.height)

    @classmethod
    def updated(cls, image):
        return friendly_datetime(image.updated)

    def read(self, request):
        rows = int(request.GET['rows'])
        page = int(request.GET['page'])
        if 'filename' in request.GET:
            filename = request.GET['filename']
        else:
            filename = ''
        limit = page*rows
        offset = (page-1)*rows
        order_by = request.GET['sidx']
        order_reversed = (request.GET['sord'] == 'desc')  #desc or asc
        if order_by == 'updated':
            order_clause = 'updated'
        elif order_by == 'filename':
            order_clause = 'image'
        elif order_by == 'size':
            order_clause = 'width'

        if order_reversed:
            order_clause = '-%s' % order_clause

        images = Image.objects.filter(image__icontains=filename).order_by(order_clause)[offset:limit]
        return images
