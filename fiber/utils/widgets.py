import json

from warnings import warn

from django import forms
from django.contrib.admin.widgets import AdminFileWidget
from django.db.models.fields.files import ImageFieldFile
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from fiber.app_settings import DETAIL_THUMBNAIL_OPTIONS
from fiber.utils.images import get_thumbnail, ThumbnailException


class FiberTextarea(forms.Textarea):

    def render(self, name, value, attrs=None, renderer=None):
        attrs['class'] = 'fiber-editor'
        return super().render(name, value, attrs, renderer)


class FiberCombobox(forms.Select):

    def render(self, name, value, attrs=None, renderer=None):
        attrs['class'] = 'fiber-combobox'
        return super().render(name, value, attrs, renderer)


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

        super().__init__(**kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        attrs['class'] = 'fiber-jsonwidget'
        if isinstance(value, dict):
            value = json.dumps(value)

        schema = self.schema

        if self.prefill_from:
            # add keys that are also used in Current table
            path = self.prefill_from
            try:
                l = path.rfind('.')
                parent, child = path[:l], path[l + 1:]
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
            var schema = {};
        }
        schema['%(name)s'] = %(json)s;
        </script>
        ''' % {
            'name': name,
            'json': json.dumps(schema),
        }
        output = super().render(name, value, attrs, renderer)
        return output + mark_safe(jquery)


class AdminImageWidgetWithPreview(AdminFileWidget):
    """
    A Widget for an ImageField with a preview of the current image.
    """

    def render(self, name, value, attrs=None, renderer=None):
        output = []
        if value and isinstance(value, ImageFieldFile):
            file_name = str(value)
            try:
                thumbnail = get_thumbnail(file_name, thumbnail_options=DETAIL_THUMBNAIL_OPTIONS)
                if thumbnail:
                    output.append('<img src="{}" width="{}" height="{}" />'.format(thumbnail.url, thumbnail.width,
                                                                                      thumbnail.height))
            except ThumbnailException as e:
                output.append(f'<p>{str(e)}</p>')
        output.append(super().render(name, value, attrs, renderer))
        return mark_safe(''.join(output))
