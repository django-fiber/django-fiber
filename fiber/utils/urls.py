from django.core.urlresolvers import reverse, NoReverseMatch


def get_admin_change_url(instance):
    """
    Return url for editing this instance in the admin.
    """
    named_url = 'admin:%s_%s_change' % (instance._meta.app_label, instance._meta.object_name.lower())
    return reverse(named_url, args=(instance.pk,))


def is_quoted_url(quoted_url):
    return quoted_url.startswith('"') and quoted_url.endswith('"')


def get_named_url_from_quoted_url(quoted_url):
    if is_quoted_url(quoted_url):
        named_url = quoted_url.strip('"')
        try:
            return reverse(named_url)
        except NoReverseMatch:
            return False
    else:
        return False
