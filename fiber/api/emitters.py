import math
from django.utils import simplejson
from django.core.serializers.json import DateTimeAwareJSONEncoder

from piston.emitters import Emitter

from fiber.models import File, Image


class jqGridJSONEmitter(Emitter):
    """
    JSON emitter, understands timestamps, wraps result set in object literal
    for jqGrid JS compatibility
    """

    def render(self, request):
        callback = request.GET.get('callback')

        row_data = self.construct()
        fields = list(self.fields)
        fields.remove('id')
        rows = [{
            'id': row['id'],
            'cell': [row[field] for field in fields]} for row in row_data]

        # todo: Is there a better way to determine this?
        if fields[1] == 'image':
            total = int(math.ceil(len(Image.objects.all())/50.0))
        else:
            total = int(math.ceil(len(File.objects.all())/50.0))

        jqgrid_dict = {'page': int(request.GET['page']), 'total': total, 'records': len(rows), 'rows': rows}
        json = simplejson.dumps(jqgrid_dict, cls=DateTimeAwareJSONEncoder, ensure_ascii=False, indent=4)

        # callback
        if callback:
            return '%s(%s)' % (callback, json)

        return json

Emitter.register('jqgrid-json', jqGridJSONEmitter, 'application/json; charset=utf-8')
