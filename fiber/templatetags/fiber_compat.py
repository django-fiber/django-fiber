from django import template

from fiber import compat

register = template.Library()


@register.tag
def url(parser, token):
    """
    Use the correct django ``url`` tag
    """
    return compat.url(parser, token)
