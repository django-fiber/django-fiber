from django import forms
from django.utils.translation import ugettext_lazy as _

from . import validators


class FiberURLField(forms.CharField):

    def __init__(self, max_length=None, min_length=None, help_text=None, *args, **kwargs):
        kwargs['help_text'] = kwargs.get('help_text', _("""Example: 'products' or '/section-1/products/' or '"some_named_url"'"""))
        super(FiberURLField, self).__init__(max_length, min_length, *args, **kwargs)
        self.validators.append(validators.FiberURLValidator())
