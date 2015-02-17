from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
import fiber.context_processors
from fiber.context_processors import page_info
from fiber.models import Page


class TestPageInfo(TestCase):
    client_class = RequestFactory

    def setUp(self):
        self.root = Page.objects.create(title='root', url='/')
        self.about = Page.objects.create(title='about us', parent=self.root, url='/about/')
        self.contact = Page.objects.create(title='contact', parent=self.about, url='/about/contact/')
        self.hidden = Page.objects.create(title='hidden', parent=self.root, url='/hidden/', is_public=False)
        self._exclude_urls = fiber.context_processors.EXCLUDE_URLS
        fiber.context_processors.EXCLUDE_URLS = [
            '^about/contact/'
        ]

    def tearDown(self):
        fiber.context_processors.EXCLUDE_URLS = self._exclude_urls

    def test_for_root(self):
        request = self.client.get(self.root.url)
        request.user = AnonymousUser()
        self.assertEqual(page_info(request), {'fiber_page': self.root, 'fiber_current_pages': []})

    def test_for_about(self):
        request = self.client.get(self.about.url)
        request.user = AnonymousUser()
        self.assertEqual(page_info(request), {'fiber_page': self.about, 'fiber_current_pages': [self.about]})

    def test_for_hidden(self):
        request = self.client.get(self.hidden.url)
        request.user = AnonymousUser()
        self.assertEqual(page_info(request), {})

    def test_for_exclude(self):
        request = self.client.get(self.contact.url)
        request.user = AnonymousUser()
        self.assertEqual(page_info(request), {})
