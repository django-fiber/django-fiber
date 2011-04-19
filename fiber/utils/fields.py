from django.db import models
from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS

from fiber import editor

from widgets import FiberTextarea


class FiberTextField(models.TextField):
    def formfield(self, **kwargs):
        defaults = {'widget': FiberTextarea}
        defaults.update(kwargs)
        return super(FiberTextField, self).formfield(**defaults)


class FiberMarkupField(FiberTextField):
    def pre_save(self, model_instance, add):
        value = super(FiberMarkupField, self).pre_save(model_instance, add)

        if editor.renderer:
            # also save html
            html_field_name = self.name.replace('_markup', '_html')
            setattr(model_instance, html_field_name, editor.renderer(value))
        return value


class FiberHTMLField(FiberTextField):
    def pre_save(self, model_instance, add):
        if not editor.renderer:
            return super(FiberHTMLField, self).pre_save(model_instance, add)
        else:
            # render the markup to get the html
            markup_field_name = self.name.replace('_html', '_markup')
            markup = getattr(model_instance, markup_field_name)
            return editor.renderer(markup)


FORMFIELD_FOR_DBFIELD_DEFAULTS[FiberMarkupField] = {'widget': FiberTextarea}
FORMFIELD_FOR_DBFIELD_DEFAULTS[FiberHTMLField] = {'widget': FiberTextarea}

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], [
        '^fiber\.utils\.fields\.FiberMarkupField',
        '^fiber\.utils\.fields\.FiberHTMLField'
    ])
except ImportError:
    pass
