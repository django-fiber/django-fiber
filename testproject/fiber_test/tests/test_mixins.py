from django.views.generic import View
from django.test import TestCase

from fiber.mixins import FiberPageMixin
from fiber.models import Page


class TestFiberPageMixin(TestCase):

    def setUp(self):
        """
        Generate test data
        """
        self.a = Page.objects.create(title='a')
        self.aa = Page.objects.create(title='aa', parent=self.a, url='aa')
        Page.objects.create(title='ab', parent=self.a, url='ab')
        self.aaa = Page.objects.create(title='aaa', parent=self.aa, url='aaa')

    def test_current_pages(self):
        """
        `get_fiber_current_pages` must return the correct list of pages that are marked as
        current.
        """
        class TestView(FiberPageMixin, View):
            def get_fiber_page_url(self):  # FiberPageMixin requires this method
                # mock a request
                return self.url

        view = TestView()
        view.url = 'aa'
        # There should be no root node, but we do want a page; aa
        self.assertEqual([self.aa], view.get_fiber_current_pages())

        view = TestView()
        view.url = 'aaa'
        # again no root node but we do want to pages; aa -> aaa
        self.assertEqual([self.aa, self.aaa], view.get_fiber_current_pages())

    # TODO write tests for `mark_current_regexes` behavior
