from django.core.exceptions import ImproperlyConfigured
from django.views.generic import View
from django.test import TestCase, SimpleTestCase

from fiber.mixins import FiberPageMixin
from fiber.models import Page


class CustomContextView(View):
    def get_context_data(self, **kwargs):
        context = {'foo': 'bar'}
        context.update(kwargs)
        return context


class TestContext(FiberPageMixin):
    pass


class TestView(FiberPageMixin, CustomContextView):
    pass


class TestGetFiberPageUrlNotImplemented(SimpleTestCase):
    def test_fiber_page_url_not_defined(self):
        """Raises ImproperlyConfigured when get_fiber_page_url is not implemented and fiber_page_url is not defined"""
        with self.assertRaises(ImproperlyConfigured) as cm:
            TestView().get_fiber_page_url()
        self.assertEqual(
            str(cm.exception), 'fiber_test.tests.test_mixins.test_fiberpagemixin.TestView is missing a fiber_page_url.'
                               ' Define TestView.fiber_page_url, or override TestView.get_fiber_page_url().')

    def test_fiber_page_url_defined(self):
        """Returns the given fiber_page_url if it's defined"""
        view = TestView()
        view.fiber_page_url = '/'
        self.assertEqual(view.get_fiber_page_url(), '/')


class TestGetCurrentPages(TestCase):
    def setUp(self):
        self.root = Page.objects.create(title='root', url='/')
        self.about = Page.objects.create(title='about us', parent=self.root, url='/about/')
        self.contact = Page.objects.create(title='contact', parent=self.about, url='/about/contact/')

    def test_get_root(self):
        """The root page is not part of the current_pages list"""
        view = TestView()
        view.fiber_page_url = '/'
        self.assertEqual([], view.get_fiber_current_pages())

    def test_get_about(self):
        """Should return the current page and nothing else since root is its only ancestor"""
        view = TestView()
        view.fiber_page_url = '/about/'
        self.assertEqual([self.about], view.get_fiber_current_pages())

    def test_get_contact(self):
        """Should return the current page, its ancestor but not root"""
        view = TestView()
        view.fiber_page_url = '/about/contact/'
        self.assertEqual([self.about, self.contact], view.get_fiber_current_pages())

    def test_hardcoded(self):
        view = TestView()
        view.fiber_current_pages = [self.root]
        self.assertEqual([self.root], view.get_fiber_current_pages())


class TestGetCurrentPagesWithMarkCurrentRegexes(TestCase):
    def setUp(self):
        self.root = Page.objects.create(title='root', url='/')
        self.about = Page.objects.create(title='about us', parent=self.root, url='/about/')
        self.contact = Page.objects.create(title='contact', parent=self.about, url='/about/contact/', mark_current_regexes='^/news/')
        self.news = Page.objects.create(title='news', parent=self.root, url='/news/', mark_current_regexes='^/about/$\n^/$')

    def test_get_root(self):
        """Should mark news as current as the url matches ^/$"""
        view = TestView()
        view.fiber_page_url = '/'
        self.assertEqual([self.news], view.get_fiber_current_pages())

    def test_get_about(self):
        """Should mark news as current as the url matches ^/about/$"""
        view = TestView()
        view.fiber_page_url = '/about/'
        self.assertEqual([self.about, self.news], view.get_fiber_current_pages())

    def test_get_contact(self):
        """Should not mark news as current as the url doesn't match ^/about/$ or ^/$"""
        view = TestView()
        view.fiber_page_url = '/about/contact/'
        self.assertEqual([self.about, self.contact], view.get_fiber_current_pages())

    def test_get_news(self):
        """Should mark about, contact as current as the url matches mark_current_regexes for contact"""
        view = TestView()
        view.fiber_page_url = '/news/'
        self.assertEqual([self.about, self.contact, self.news], view.get_fiber_current_pages())

    def test_get_contact_with_archive(self):
        """Mark current regexes also adds parents to current_pages"""
        archive = Page.objects.create(title='archive', parent=self.news, url='/news/archive/', mark_current_regexes='^/about/contact/')
        view = TestView()
        view.fiber_page_url = '/about/contact/'
        self.assertEqual([self.about, self.contact, self.news, archive], view.get_fiber_current_pages())


class TestGetContextData(TestCase):
    """Test get_context_data, super object does NOT implement get_context_data"""
    view_class = TestContext
    extra_context = {}

    def setUp(self):
        self.root = Page.objects.create(title='root', url='/')
        self.child = Page.objects.create(title='child', parent=self.root, url='/child/')
        self.grandchild = Page.objects.create(title='grandchild', parent=self.child, url='/child/grandchild/')

    def test_get_root(self):
        view = self.view_class()
        view.fiber_page_url = '/'
        expected = {
            'fiber_page': self.root,
            'fiber_current_pages': []
        }
        expected.update(self.extra_context)
        self.assertEqual(expected, view.get_context_data())

    def test_get_first_child(self):
        view = self.view_class()
        view.fiber_page_url = '/child/'
        expected = {
            'fiber_page': self.child,
            'fiber_current_pages': [self.child]
        }
        expected.update(self.extra_context)
        self.assertEqual(expected, view.get_context_data())

    def test_get_current_pages_with_ancestors(self):
        view = self.view_class()
        view.fiber_page_url = '/child/grandchild/'
        expected = {
            'fiber_page': self.grandchild,
            'fiber_current_pages': [self.child, self.grandchild]
        }
        expected.update(self.extra_context)
        self.assertEqual(expected, view.get_context_data())


class TestGetContextWithSuper(TestGetContextData):
    """Test get_context_data, super object DOES implements get_context_data"""
    view_class = TestView
    extra_context = {'foo': 'bar'}
