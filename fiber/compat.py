import django

# import the url templatetag from the correct module
if django.VERSION < (1, 5):
    from django.templatetags.future import url
else:
    from django.template.defaulttags import url


# import model_ngettext from the correct module
if django.VERSION < (1, 7):
    from django.contrib.admin.util import model_ngettext
else:
    from django.contrib.admin.utils import model_ngettext
