from django.contrib.auth.models import User
from django.template import Template, Context, TemplateSyntaxError
from django.test import TestCase, SimpleTestCase
from django.urls import reverse

from fiber.models import Page, ContentItem, PageContentItem
from ...test_util import RenderMixin


class TestShowPageContent(RenderMixin, TestCase):
    def setUp(self):
        self.home = Page.objects.create(title='Home')
        self.home_content = home = ContentItem.objects.create(content_html='<p>homepage</p>')
        self.home_page_content = PageContentItem.objects.create(content_item=home, page=self.home, block_name='main')
        self.about = Page.objects.create(title='About')
        self.about_content = about = ContentItem.objects.create(content_html='<p>about</p>')
        self.about_page_content = PageContentItem.objects.create(content_item=about, page=self.about, block_name='main')
        # Staff user
        self.staff = User.objects.create_user('staff', 'staff@example.com', password='staff')
        self.staff.is_staff = True
        self.staff.save()

    def test_show_page_content(self):
        self.assertRendered(
            '{% load fiber_tags %}{% show_page_content "main" %}',
            '<div><div class="content"><p>homepage</p></div></div>',
            {'fiber_page': self.home})

    def test_show_page_content_for_staff(self):
        self.assertRendered(
            '{% load fiber_tags %}{% show_page_content "main" %}',
            '''
            <div data-fiber-data='{ "can_edit":true, "type": "content_item", "add_url": "%(add_url)s", "page_id": %(home_pk)s, "block_name": "main" }'>
                <div data-fiber-data='{ "can_edit": true, "type": "content_item", "id": %(home_content_pk)s, "url": "%(edit_url_home_content)s", "add_url": "%(add_url)s", "page_id": %(home_pk)s, "block_name": "main", "page_content_item_id": %(home_page_content_pk)s, "used_on_pages": [{&quot;title&quot;: &quot;Home&quot;, &quot;url&quot;: &quot;&quot;}] }' class="content">
                    <p>homepage</p>
                </div>
            </div>''' % {
                'home_pk': self.home.pk,
                'add_url': reverse('fiber_admin:fiber_contentitem_add'),
                'home_page_content_pk': self.home_page_content.pk,
                'home_content_pk': self.home_content.pk,
                'edit_url_home_content': reverse('fiber_admin:fiber_contentitem_change', args=[self.home_content.pk])
            }, {'fiber_page': self.home, 'user': self.staff})

    def test_show_page_content_with_other(self):
        """The show_page_content templatetag should support rendering content from multiple pages in one view."""
        self.assertRendered(
            '{% load fiber_tags %}{% show_page_content about_page "main" %}{% show_page_content "main" %}',
            '<div><div class="content"><p>about</p></div></div><div><div class="content"><p>homepage</p></div></div>',
            {'fiber_page': self.home, 'about_page': self.about})

    def test_show_page_content_with_other_for_staff(self):
        self.assertRendered(
            '{% load fiber_tags %}{% show_page_content about_page "main" %}{% show_page_content "main" %}',
            '''
            <div data-fiber-data='{ "can_edit":true, "type": "content_item", "add_url": "%(add_url)s", "page_id": %(about_pk)s, "block_name": "main" }'>
                <div data-fiber-data='{ "can_edit": true, "type": "content_item", "id": %(about_content_pk)s, "url": "%(edit_url_about_content)s", "add_url": "%(add_url)s", "page_id": %(about_pk)s, "block_name": "main", "page_content_item_id": %(about_page_content_pk)s, "used_on_pages": [{&quot;title&quot;: &quot;About&quot;, &quot;url&quot;: &quot;&quot;}] }' class="content">
                    <p>about</p>
                </div>
            </div>
            <div data-fiber-data='{ "can_edit":true, "type": "content_item", "add_url": "%(add_url)s", "page_id": %(home_pk)s, "block_name": "main" }'>
                <div data-fiber-data='{ "can_edit": true, "type": "content_item", "id": %(home_content_pk)s, "url": "%(edit_url_home_content)s", "add_url": "%(add_url)s", "page_id": %(home_pk)s, "block_name": "main", "page_content_item_id": %(home_page_content_pk)s, "used_on_pages": [{&quot;title&quot;: &quot;Home&quot;, &quot;url&quot;: &quot;&quot;}] }' class="content">
                    <p>homepage</p>
                </div>
            </div>''' % {
                'about_pk': self.about.pk,
                'home_pk': self.home.pk,
                'add_url': reverse('fiber_admin:fiber_contentitem_add'),
                'about_page_content_pk': self.about_page_content.pk,
                'home_page_content_pk': self.home_page_content.pk,
                'about_content_pk': self.about_content.pk,
                'home_content_pk': self.home_content.pk,
                'edit_url_about_content': reverse('fiber_admin:fiber_contentitem_change', args=[self.about_content.pk]),
                'edit_url_home_content': reverse('fiber_admin:fiber_contentitem_change', args=[self.home_content.pk])
            }, {'fiber_page': self.home, 'about_page': self.about, 'user': self.staff})

    def test_single_argument_lookup(self):
        self.assertRendered(
            '{% load fiber_tags %}{% show_page_content main %}',
            '<div><div class="content"><p>homepage</p></div></div>',
            {'fiber_page': self.home, 'main': 'main'})

    def test_two_argument_lookup(self):
        self.assertRendered(
            '{% load fiber_tags %}{% show_page_content about_page main %}',
            '<div><div class="content"><p>about</p></div></div>',
            {'fiber_page': self.home, 'about_page': self.about, 'main': 'main'})

    def test_on_non_fiber_page(self):
        """
        show_page_content on a non fiber page
        """
        self.assertRendered('{% load fiber_tags %}{% show_page_content "main" %}', '')


class TestSyntaxErrors(TestCase):
    def test_with_fiber_page_but_no_block_name(self):
        """
        show_page_content with only a given fiber page
        """
        about = Page.objects.create(title='About')
        with self.assertRaises(TemplateSyntaxError) as cm:
            Template('{% load fiber_tags %}{% show_page_content about %}').render(Context({'about': about}))
        self.assertEqual(str(cm.exception), "'show_page_content' received invalid arguments")

    def test_wrong_two_arguments(self):
        """
        show_page_content with two strings cannot work
        """
        with self.assertRaises(TemplateSyntaxError) as cm:
            Template('{% load fiber_tags %}{% show_page_content "page" "main" %}').render(Context({}))
        self.assertEqual(str(cm.exception), "'show_page_content' received invalid arguments")
