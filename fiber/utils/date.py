def friendly_datetime(date_time):
    """
    Given a datetime object or an int() Unix timestamp, return a friendly
    string like 'an hour ago', 'yesterday', '3 months ago', 'just now', etc.
    """
    from datetime import datetime

    now = datetime.now()
    if type(date_time) is datetime:
        diff = now - date_time
    elif type(date_time) is int:
        diff = now - datetime.fromtimestamp(date_time)
    else:
        return date_time

    seconds_diff = diff.seconds
    days_diff = diff.days

    if days_diff < 0:
        return ''

    if days_diff == 0:
        if seconds_diff < 10:
            return 'just now'
        if seconds_diff < 60:
            return str(seconds_diff) + ' seconds ago'
        if seconds_diff < 120:
            return  'a minute ago'
        if seconds_diff < 3600:
            return str(seconds_diff / 60) + ' minutes ago'
        if seconds_diff < 7200:
            return 'an hour ago'
        if seconds_diff < 86400:
            return str(seconds_diff / 3600) + ' hours ago'
    if days_diff == 1:
        return 'yesterday'
    if days_diff < 7:
        return str(days_diff) + ' days ago'
    if days_diff < 31:
        return str(days_diff / 7) + ' weeks ago'
    if days_diff < 365:
        return str(days_diff / 30) + ' months ago'
    return str(days_diff / 365) + ' years ago'
