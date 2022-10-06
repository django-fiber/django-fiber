from django.urls import reverse, NoReverseMatch


def get_admin_change_url(instance):
    """
    Return url for editing this instance in the admin.
    """
    named_url = f'admin:{instance._meta.app_label}_{instance._meta.object_name.lower()}_change'
    return reverse(named_url, args=(instance.pk,))


# PageManager.get_by_url duplicates this logic for efficient DB use
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
