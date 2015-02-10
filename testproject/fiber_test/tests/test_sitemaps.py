from django.test import TestCase

from fiber.sitemaps import FiberSitemap
from fiber.models import Page


class TestSitemap(TestCase):

    def setUp(self):
        """
        Generate test data.
        """
        self.a = Page.objects.create(title='a')
        self.aa = Page.objects.create(title='aa', parent=self.a, url='aa')

    def test_sitemap_class(self):
        """
        Sitemap class should list the 2 test pages.
        """

        urls = FiberSitemap().get_urls()
        self.assertEqual(len(urls), 2)

    def test_public(self):
        """
        Only public pages go in the sitemap.
        """

        self.a.is_public = False
        self.a.save()

        urls = FiberSitemap().get_urls()
        self.assertEqual(len(urls), 1)
