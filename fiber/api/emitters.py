import math
from django.utils import simplejson
from django.core.serializers.json import DateTimeAwareJSONEncoder

from piston.emitters import Emitter

from fiber.models import File, Image


class DataGridJSONEmitter(Emitter):
    """
    JSON emitter, understands timestamps, wraps result set in object literal
    for fiber-datagrid JS compatibility
    """
    def render(self, request):
        callback = request.GET.get('callback')

        row_data = self.construct()
        fields = list(self.fields)
        fields.remove('id')

        # todo: Is there a better way to determine this?
        rows_per_page = 10
        if fields[1] == 'image':
            total = int(math.ceil(len(Image.objects.all())/(rows_per_page * 1.0)))
        else:
            total = int(math.ceil(len(File.objects.all())/(rows_per_page * 1.0)))

        data = dict(
            total_pages=total,
            rows=row_data
        )
        json = simplejson.dumps(data, cls=DateTimeAwareJSONEncoder, ensure_ascii=False, indent=4)

        # callback
        if callback:
            return '%s(%s)' % (callback, json)

        return json

Emitter.register('datagrid-json', DataGridJSONEmitter, 'application/json; charset=utf-8')
