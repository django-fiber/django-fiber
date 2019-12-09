import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, URLValidator
from django.utils.encoding import smart_str
from django.utils.translation import gettext_lazy as _

from .urls import get_named_url_from_quoted_url, is_quoted_url


class FiberURLValidator(RegexValidator):
    """
    This class provides custom validation - required for Fiber's specific context.
    Django's `URLValidator` only matches urls that are prefixed with a protocol.
    """
    protocol_regex = re.compile(r'^(((http|ftp)s?)://).+$', re.IGNORECASE)
    regex = re.compile(r'^[-\w/\.\:#\?&"=]+$')

    def __call__(self, value):
        """
        Validates that the input matches the regular expression.
        """
        url = smart_str(value)
        # check if it starts with http(s):// | ftp(s)://
        # Django's validator only works with full urls that include a protocol.
        if self.protocol_regex.search(url):
            django_url_validator = URLValidator()
            django_url_validator(url)
        else:
            # check if it's a named url, and if so, if it's reversible
            if is_quoted_url(url) and not get_named_url_from_quoted_url(url):
                raise ValidationError(_('No reverse match found for the named url'), 'no_reverse_match')
            # check if it's a fiber_url (more strict than absolute url)
            if not self.regex.search(url):
                raise ValidationError(self.message, code=self.code)
