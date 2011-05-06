import os
from fiber.models import File
from piston.handler import BaseHandler
from piston.utils import rc
from fiber.utils.date import friendly_datetime


class FileHandler(BaseHandler):
    allowed_methods = ('GET', )
    fields = ('id', 'url', 'filename', 'updated')
    exclude = () # un-exclude `id`
    model = File

    @classmethod
    def url(cls, file):
        return file.file.url

    @classmethod
    def filename(cls, file):
        return os.path.basename(file.file.name)

    @classmethod
    def updated(cls, file):
        return friendly_datetime(file.updated)

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
            order_clause = 'file'

        if order_reversed:
            order_clause = '-%s' % order_clause

        files = File.objects.filter(file__icontains=filename).order_by(order_clause)[offset:limit]

        return files

    def create(self, request):
        File.objects.create(
            file=request.FILES['file'],
            title='uploaded',  # TODO: empty title
        )
        return rc.CREATED
