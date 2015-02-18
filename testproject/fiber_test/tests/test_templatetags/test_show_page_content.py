from django.template import Template, Context, TemplateSyntaxError
from django.test import TestCase

from fiber.models import Page, ContentItem, PageContentItem
from ...test_util import RenderMixin


class TestShowPageContent(RenderMixin, TestCase):
    def setUp(self):
        self.home = Page.objects.create(title='Home')
        home = ContentItem.objects.create(content_html='<p>homepage</p>')
        PageContentItem.objects.create(content_item=home, page=self.home, block_name='main')
        self.about = Page.objects.create(title='About')
        about = ContentItem.objects.create(content_html='<p>about</p>')
        PageContentItem.objects.create(content_item=about, page=self.about, block_name='main')

    def test_show_page_content(self):
        self.assertRendered(
            '{% load fiber_tags %}{% show_page_content "main" %}',
            '<div><div class="content"><p>homepage</p></div></div>',
            context={'fiber_page': self.home})

    def test_show_page_content_with_other(self):
        """The show_page_content templatetag should support rendering content from multiple pages in one view."""
        self.assertRendered(
            '{% load fiber_tags %}{% show_page_content about_page "main" %}{% show_page_content "main" %}',
            '<div><div class="content"><p>about</p></div></div><div><div class="content"><p>homepage</p></div></div>',
            context={'fiber_page': self.home, 'about_page': self.about})

    def test_too_little_arguments(self):
        with self.assertRaises(TemplateSyntaxError) as cm:
            Template('{% load fiber_tags %}{% show_page_content %}').render(Context({}))
        self.assertEqual(str(cm.exception), "'show_page_content' did not receive value(s) for the argument(s): 'page_or_block_name'")

    def test_too_many_arguments(self):
        with self.assertRaises(TemplateSyntaxError) as cm:
            Template('{% load fiber_tags %}{% show_page_content "page" "main" "other" %}').render(Context({}))
        self.assertEqual(str(cm.exception), "'show_page_content' received too many positional arguments")

    def test_wrong_single_argument(self):
        with self.assertRaises(TemplateSyntaxError) as cm:
            Template('{% load fiber_tags %}{% show_page_content page %}').render(Context({}))
        self.assertEqual(str(cm.exception), "'show_page_content' requires 'fiber_page' to be in the template context")

    def test_wrong_two_arguments(self):
        with self.assertRaises(TemplateSyntaxError) as cm:
            Template('{% load fiber_tags %}{% show_page_content "page" "main" %}').render(Context({}))
        self.assertEqual(str(cm.exception), "'show_page_content' received invalid arguments")

    def test_single_argument_lookup(self):
        self.assertRendered(
            '{% load fiber_tags %}{% show_page_content main %}',
            '<div><div class="content"><p>homepage</p></div></div>',
            context={'fiber_page': self.home, 'main': 'main'})

    def test_two_argument_lookup(self):
        self.assertRendered(
            '{% load fiber_tags %}{% show_page_content about_page main %}',
            '<div><div class="content"><p>about</p></div></div>',
            context={'fiber_page': self.home, 'about_page': self.about, 'main': 'main'})
