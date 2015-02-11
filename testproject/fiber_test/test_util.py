import re
from datetime import datetime

import django
from django.conf import settings

try:
    from django.utils.timezone import make_aware, utc
except ImportError:
    pass


def get_short_django_version():
    """
    Get first two numbers of Django version.
    E.g. (1, 5)
    """
    return django.VERSION[0:2]


def format_list(l, must_sort=True, separator=' '):
    """
    Format a list as a string. Default the items in the list are sorted.
    E.g.
    >>> format_list([3, 2, 1])
    u'1 2 3'
    """
    titles = [unicode(v) for v in l]
    if must_sort:
        titles = sorted(titles)

    return separator.join(titles)


def condense_html_whitespace(s):
    s = re.sub("\s\s*", " ", s)
    s = re.sub(">\s*<", "><", s)
    s = re.sub(" class=\"\s?(.*?)\s?\"", " class=\"\\1\"", s)
    s = s.strip()
    return s


def mock_tz_now():
    """
    Return january 15 2013 10:30

    Depending on the Django version and the settings it will return a datetime with or without timezone.
    """
    result = datetime(2013, 1, 15, 10, 30)

    if get_short_django_version() >= (1, 4) and settings.USE_TZ:
        return make_aware(result, utc)
    else:
        return result
