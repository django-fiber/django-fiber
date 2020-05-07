from django import forms
from django.utils.translation import gettext_lazy as _

from . import validators


class FiberURLField(forms.CharField):
    def __init__(self, help_text=None, *args, **kwargs):
        kwargs['help_text'] = kwargs.get('help_text',
                                         _("""Example: 'products' or '/section-1/products/' or '"some_named_url"'"""))
        super().__init__(*args, **kwargs)
        self.validators.append(validators.FiberURLValidator())
