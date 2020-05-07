import json

from django import forms
from django.db import models
from django.utils.encoding import force_str

from .widgets import JSONWidget


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

        super().__init__(**kwargs)

    def clean(self, value):
        if not value:
            return None
        try:
            return json.loads(value)
        except Exception as exception:
            raise forms.ValidationError('JSON decode error: %s' % force_str(exception))


class JSONField(models.TextField):
    def __init__(self, *args, **kwargs):

        if 'schema' in kwargs:
            self.schema = kwargs.pop('schema')
        else:
            self.schema = {}

        if 'prefill_from' in kwargs:
            self.prefill_from = kwargs.pop('prefill_from')
        else:
            self.prefill_from = None

        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['schema'] = self.schema
        kwargs['prefill_from'] = self.prefill_from
        return super().formfield(form_class=JSONFormField, **kwargs)

    def to_python(self, value):
        if value is None:
            return None
        try:
            if isinstance(value, str):
                return json.loads(value)
        except ValueError:
            pass
        return value

    def _get_json_value(self, value):
        if value is None:
            return ''
        elif isinstance(value, str):
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
        return super().get_db_prep_save(value, *args, **kwargs)

    def from_db_value(self, value, *args, **kwargs):
        return self.to_python(value)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self._get_json_value(value)
