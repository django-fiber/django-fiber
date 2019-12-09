import re

from django.template import Template, Context
from django.utils.encoding import force_str

try:
    from django.utils.timezone import make_aware, utc
except ImportError:
    make_aware, utc = None, None


def format_list(l, must_sort=True, separator=' '):
    """
    Format a list as a string. Default the items in the list are sorted.
    E.g.
    >>> format_list([3, 2, 1])
    '1 2 3'
    """
    titles = [force_str(v) for v in l]
    if must_sort:
        titles = sorted(titles)

    return separator.join(titles)


def condense_html_whitespace(s):
    s = re.sub(r'\s+', " ", s)
    s = re.sub(r'>\s+<', "><", s)
    s = re.sub(r' class="\s*(.*?)\s*"', r' class="\1"', s)
    s = s.strip()
    return s


class RenderMixin:
    def assertRendered(self, template, expected, context=None):
        t, c = Template(template), Context(context or {})
        self.assertEqual(condense_html_whitespace(t.render(c)), condense_html_whitespace(expected))
