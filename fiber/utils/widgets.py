from django import forms
from django.utils import simplejson as json
from django.utils.safestring import mark_safe
from warnings import warn


class FiberTextarea(forms.Textarea):

    def render(self, name, value, attrs=None):
        attrs['class'] = 'fiber-editor'
        return super(FiberTextarea, self).render(name, value, attrs)


class FiberCombobox(forms.Select):

    def render(self, name, value, attrs=None):
        attrs['class'] = 'fiber-combobox'
        return super(FiberCombobox, self).render(name, value, attrs)


class JSONWidget(forms.Textarea):

    def __init__(self, **kwargs):
        if 'schema' in kwargs:
            self.schema = kwargs.pop('schema')
        else:
            self.schema = {}

        if 'prefill_from' in kwargs:
            self.prefill_from = kwargs.pop('prefill_from')
        else:
            self.prefill_from = None

        super(JSONWidget, self).__init__(**kwargs)

    def render(self, name, value, attrs=None):
        attrs['class'] = 'fiber-jsonwidget'
        if isinstance(value, dict):
            value = json.dumps(value)

        schema = self.schema

        if self.prefill_from:
            # add keys that are also used in Current table
            path = self.prefill_from
            try:
                l = path.rfind('.')
                parent, child = path[:l], path[l+1:]
                base = __import__(parent, globals(), globals(), [child])
                dynamic_class = getattr(base, child, None)
                all_keys = []
                objects = dynamic_class.objects.filter(**{"%s__isnull" % name: False})
                for obj in objects:
                    for key in getattr(obj, 'metadata'):
                        all_keys.append(key)
                all_keys = list(set(all_keys))
                for key in all_keys:
                    if key not in schema:
                        schema[key] = {
                                'widget': 'textfield',
                        }
            except AttributeError:
                warn('The path for prefill_from field "%s" is incorrect!' % path)
        jquery = '''
        <script type="text/javascript">
        if (schema == null) {
            var schema = [];
        }
        schema['%(name)s'] = %(json)s;
        </script>
        ''' % {
            'name': name,
            'json': json.dumps(schema),
        }
        output = super(JSONWidget, self).render(name, value, attrs)
        return output + mark_safe(jquery)
