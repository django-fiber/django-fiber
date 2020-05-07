r"""
The `Sitemaps protocol <http://en.wikipedia.org/wiki/Sitemaps>`_ allows a webmaster
to inform search engines about URLs on a website that are available for crawling.
Django comes with a high-level framework that makes generating sitemap XML files easy.

Install the sitemap application as per the `instructions in the django documentation
<https://docs.djangoproject.com/en/dev/ref/contrib/sitemaps/>`_, then edit your
project's ``urls.py`` and add a reference to Fiber's Sitemap class in order to
included all the publicly-viewable Fiber pages:

.. code-block:: python

    ...
    from fiber.sitemaps import FiberSitemap
    ...
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'fiber': FiberSitemap,
                                                                  ... other sitemaps... })
    ...
"""
from django.contrib.sitemaps import Sitemap

from .models import Page


class FiberSitemap(Sitemap):

    changefreq = 'monthly'

    def items(self):
        return Page.objects.filter(is_public=True)

    def lastmod(self, obj):
        return obj.updated
