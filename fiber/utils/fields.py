from django.db import models
from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS
from django.utils.translation import ugettext_lazy as _

from fiber import editor

from . import form_fields
from . import validators
from .widgets import FiberTextarea


class FiberURLField(models.CharField):
    description = _('URL')

    def __init__(self, verbose_name=None, name=None, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 255)
        super().__init__(verbose_name, name, **kwargs)
        self.validators.append(validators.FiberURLValidator())

    def formfield(self, **kwargs):
        defaults = {
            'form_class': form_fields.FiberURLField,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)


class FiberTextField(models.TextField):
    def formfield(self, **kwargs):
        defaults = {'widget': FiberTextarea}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class FiberMarkupField(FiberTextField):
    def pre_save(self, model_instance, add):
        value = super().pre_save(model_instance, add)

        if editor.renderer:
            # also save html
            html_field_name = self.name.replace('_markup', '_html')
            setattr(model_instance, html_field_name, editor.renderer(value))
        return value


class FiberHTMLField(FiberTextField):
    def pre_save(self, model_instance, add):
        if not editor.renderer:
            return super().pre_save(model_instance, add)
        else:
            # render the markup to get the html
            markup_field_name = self.name.replace('_html', '_markup')
            markup = getattr(model_instance, markup_field_name)
            return editor.renderer(markup)


FORMFIELD_FOR_DBFIELD_DEFAULTS[FiberMarkupField] = {'widget': FiberTextarea}
FORMFIELD_FOR_DBFIELD_DEFAULTS[FiberHTMLField] = {'widget': FiberTextarea}
