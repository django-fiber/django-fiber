from django.core.urlresolvers import reverse
from django.template import Template, Context, TemplateSyntaxError
from django.test import TestCase, SimpleTestCase
from django.contrib.auth.models import User, AnonymousUser
import fiber

from fiber.models import Page, ContentItem, PageContentItem
from ..test_util import condense_html_whitespace


class RenderMixin(object):
    def assertRendered(self, template, expected, context=None):
        t, c = Template(template), Context(context or {})
        self.assertEqual(condense_html_whitespace(t.render(c)), condense_html_whitespace(expected))


class TestShowMenu(RenderMixin, TestCase):
    def setUp(self):
        main = Page.objects.create(title='main')
        self.home = Page.objects.create(title='home', parent=main, url='/')
        self.about = Page.objects.create(title='about', parent=self.home, url='about')
        self.news = Page.objects.create(title='news', parent=self.home, url='news')
        self.contact = Page.objects.create(title='contact', parent=self.about, url='contact')
        self.jobs = Page.objects.create(title='jobs', parent=self.about, url='jobs')

    def get_non_staff_user(self):
        return AnonymousUser()

    def get_staff_user(self):
        user = User.objects.create_user('user2', 'u2@ser.nl', password="secure")
        user.is_staff = True
        return user

    def test_show_user_menu_all(self):
        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 1 999 "all" %}',
                '''
                <ul>
                    <li class="home first last">
                        <a href="/">home</a>
                        <ul>
                            <li class="about first">
                                <a href="/about/">about</a>
                                <ul>
                                    <li class="contact first"><a href="/about/contact/">contact</a></li>
                                    <li class="jobs last"><a href="/about/jobs/">jobs</a></li>
                                </ul>
                            </li>
                            <li class="news last"><a href="/news/">news</a></li>
                        </ul>
                    </li>
                </ul>''', {
                    'user': self.get_non_staff_user(),
                    'fiber_page': self.home,
                })

    def test_show_user_menu_all_descendants(self):
        """Tests for 'all_descendants' with a minimum level"""
        user = self.get_non_staff_user()

        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 2 999 "all_descendants" %}',
                '''
                <ul>
                    <li class="about first">
                        <a href="/about/">about</a>
                        <ul>
                            <li class="contact first"><a href="/about/contact/">contact</a></li>
                            <li class="jobs last"><a href="/about/jobs/">jobs</a></li>
                        </ul>
                    </li>
                    <li class="news last">
                        <a href="/news/">news</a>
                    </li>
                 </ul>''', {
                    'user': user,
                    'fiber_page': self.about,
                })

        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 2 999 "all_descendants" %}',
                '''
                <ul>
                    <li class="about first"><a href="/about/">about</a></li>
                    <li class="news last"><a href="/news/">news</a></li>
                </ul>''', {
                    'user': user,
                    'fiber_page': self.news,
                })

    def test_show_user_menu_min_max_level(self):
        """Test for minimum and maximum level"""
        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 2 2 %}',
                '''
                <ul>
                    <li class="about first"><a href="/about/">about</a></li>
                    <li class="news last"><a href="/news/">news</a></li>
                </ul>''', {
                    'user': self.get_non_staff_user(),
                    'fiber_page': self.contact,
                })

        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 3 3 %}',
                '''
                <ul>
                    <li class="contact first"><a href="/about/contact/">contact</a></li>
                    <li class="jobs last"><a href="/about/jobs/">jobs</a></li>
                </ul>''', {
                    'user': self.get_non_staff_user(),
                    'fiber_page': self.contact,
                })

    def test_show_user_menu_different_root(self):
        """Test that show_menu only shows top level if current page is in different root"""
        other_root = Page.objects.create(title='other')

        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 1 999 %}',
                '''
                <ul>
                    <li class="home first last"><a href="/">home</a></li>
                </ul>''', {
                    'user': self.get_non_staff_user(),
                    'fiber_page': other_root,
                })

    def test_show_staff_menu_all(self):
        """Render menu with all pages for staff user"""
        user = self.get_staff_user()

        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 1 999 "all" %}',
                '''
                <ul data-fiber-data='{ "type": "page", "add_url": "%(fiber_admin_page_add_url)s", "parent_id": 1 }'>
                    <li class="home first last">
                        <a href="/" data-fiber-data='{ "can_edit": true, "type": "page", "id": 2, "parent_id": 1, "url": "%(fiber_admin_page_edit_url_home)s", "add_url": "%(fiber_admin_page_add_url)s" }'>home</a>
                        <ul data-fiber-data='{ "type": "page", "add_url": "%(fiber_admin_page_add_url)s", "parent_id": 2 }'>
                            <li class="about first">
                                <a href="/about/" data-fiber-data='{ "can_edit": true, "type": "page", "id": 3, "parent_id": 2, "url": "%(fiber_admin_page_edit_url_about)s", "add_url": "%(fiber_admin_page_add_url)s" }'>about</a>
                                <ul data-fiber-data='{ "type": "page", "add_url": "%(fiber_admin_page_add_url)s", "parent_id": 3 }'>
                                    <li class="contact first">
                                        <a href="/about/contact/" data-fiber-data='{ "can_edit": true, "type": "page", "id": 5, "parent_id": 3, "url": "%(fiber_admin_page_edit_url_contact)s", "add_url": "%(fiber_admin_page_add_url)s" }'>contact</a>
                                    </li>
                                    <li class="jobs last">
                                        <a href="/about/jobs/" data-fiber-data='{ "can_edit": true, "type": "page", "id": 6, "parent_id": 3, "url": "%(fiber_admin_page_edit_url_jobs)s", "add_url": "%(fiber_admin_page_add_url)s" }'>jobs</a>
                                    </li>
                                </ul>
                            </li>
                            <li class="news last">
                                <a href="/news/" data-fiber-data='{ "can_edit": true, "type": "page", "id": 4, "parent_id": 2, "url": "%(fiber_admin_page_edit_url_news)s", "add_url": "%(fiber_admin_page_add_url)s" }'>news</a>
                            </li>
                        </ul>
                    </li>
                </ul>''' % {
                    'fiber_admin_page_add_url': reverse('fiber_admin:fiber_page_add'),
                    'fiber_admin_page_edit_url_home': reverse('fiber_admin:fiber_page_change', args=[self.home.pk]),
                    'fiber_admin_page_edit_url_about': reverse('fiber_admin:fiber_page_change', args=[self.about.pk]),
                    'fiber_admin_page_edit_url_news': reverse('fiber_admin:fiber_page_change', args=[self.news.pk]),
                    'fiber_admin_page_edit_url_contact': reverse('fiber_admin:fiber_page_change', args=[self.contact.pk]),
                    'fiber_admin_page_edit_url_jobs': reverse('fiber_admin:fiber_page_change', args=[self.jobs.pk])
                }, {
                    'user': user,
                    'fiber_page': self.home,
                })

    def test_show_non_existing_menu(self):
        """Rendering a non-existing menu raises a specific Page.DoesNotExist exception"""
        with self.assertRaises(Page.DoesNotExist) as cm:
            Template('{% load fiber_tags %}{% show_menu "missing" 1 999 %}').render(Context())
        self.assertEqual(str(cm.exception), "Menu does not exist.\nNo top-level page found with the title 'missing'.")


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


class TestFiberVersion(RenderMixin, SimpleTestCase):
    def test_fiber_version(self):
        self.assertRendered('{% load fiber_tags %}{% fiber_version %}', str(fiber.__version__))
