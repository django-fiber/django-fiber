from datetime import datetime

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


def friendly_datetime(date_time):
    """
    Given a datetime object or an int() Unix timestamp, return a friendly
    string like 'an hour ago', 'yesterday', '3 months ago', 'just now', etc.
    """
    now = timezone.now()
    if isinstance(date_time, int):
        try:
            date_time = datetime.fromtimestamp(date_time)
        except (ValueError, OSError, OverflowError):
            pass
    if isinstance(date_time, datetime):
        if settings.USE_TZ and timezone.is_naive(date_time):
            date_time = timezone.make_aware(date_time, timezone.get_current_timezone())
        diff = now - date_time
    else:
        return date_time

    seconds_diff = diff.seconds
    days_diff = diff.days

    if days_diff < 0:
        return ''

    if days_diff == 0:
        if seconds_diff < 10:
            return _('just now')
        if seconds_diff < 60:
            return _('%s seconds ago') % seconds_diff
        if seconds_diff < 120:
            return _('a minute ago')
        if seconds_diff < 3600:
            return _('%s minutes ago') % int(seconds_diff / 60)
        if seconds_diff < 7200:
            return _('an hour ago')
        if seconds_diff < 86400:
            return _('%s hours ago') % int(seconds_diff / 3600)
    if days_diff == 1:
        return _('yesterday')
    if days_diff < 7:
        return _('%s days ago') % days_diff
    if days_diff < 14:
        return _('a week ago')
    if days_diff < 31:
        return _('%s weeks ago') % int(days_diff / 7)
    if days_diff < 365:
        months_diff = int(days_diff / 30)
        if months_diff == 1:
            return _('a month ago')
        else:
            return _('%s months ago') % int(days_diff / 30)
    years_diff = int(days_diff / 365)
    if years_diff == 1:
        return _('a year ago')
    return _('%s years ago') % int(days_diff / 365)
