from django.db import models
from django import forms
from django.utils import simplejson as json

from fiber.utils.widgets import JSONWidget


class JSONFormField(forms.CharField):

    def __init__(self, **kwargs):
        if 'schema' in kwargs:
            self.schema = kwargs.pop('schema')
        else:
            self.schema = {}

        if 'prefill_from' in kwargs:
            self.prefill_from = kwargs.pop('prefill_from')
        else:
            self.prefill_from = None

        kwargs['widget'] = JSONWidget(schema=self.schema, prefill_from=self.prefill_from)

        super(JSONFormField, self).__init__(**kwargs)

    def clean(self, value):
        if not value:
            return None
        try:
            return json.loads(value)
        except Exception, exception:
            raise forms.ValidationError(u'JSON decode error: %s' % (unicode(exception), ))


class JSONField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):

        if 'schema' in kwargs:
            self.schema = kwargs.pop('schema')
        else:
            self.schema = {}

        if 'prefill_from' in kwargs:
            self.prefill_from = kwargs.pop('prefill_from')
        else:
            self.prefill_from = None

        super(JSONField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['schema'] = self.schema
        kwargs['prefill_from'] = self.prefill_from
        return super(JSONField, self).formfield(form_class=JSONFormField, **kwargs)

    def to_python(self, value):
        if value is None:
            return None
        try:
            if isinstance(value, basestring):
                return json.loads(value)
        except ValueError:
            pass
        return value

    def _get_json_value(self, value):
        if value is None:
            return ''
        elif isinstance(value, basestring):
            return value
        else:
            return json.dumps(value)

    def get_prep_value(self, value, *args, **kwargs):
        return self._get_json_value(value)

    def get_db_prep_save(self, value, *args, **kwargs):
        if value is None:
            return None
        if isinstance(value, dict):
            value = json.dumps(value)
        return super(JSONField, self).get_db_prep_save(value, *args, **kwargs)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self._get_json_value(value)

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ['^fiber\.utils\.json\.JSONField'])
except ImportError:
    pass
