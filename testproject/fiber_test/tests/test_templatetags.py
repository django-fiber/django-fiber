from django.core.urlresolvers import reverse
from django.template import Template, Context, TemplateSyntaxError
from django.test import TestCase, SimpleTestCase
from django.contrib.auth.models import User
import fiber

from fiber.models import Page, ContentItem, PageContentItem
from ..test_util import condense_html_whitespace


class RenderMixin(object):
    def assertRendered(self, template, expected, context=None):
        self.assertEqual(condense_html_whitespace(Template(template).render(Context(context or {}))), expected)


class TestTemplateTags(TestCase):

    def setUp(self):
        """
        Generates test data
        """
        # generate data
        main = Page.objects.create(title='main')
        home = Page.objects.create(title='home', parent=main, url='/')
        section1 = Page.objects.create(title='section1', parent=home, url='section1')
        section2 = Page.objects.create(title='section2', parent=home, url='section2')
        section11 = Page.objects.create(title='sub1', parent=section1, url='sub1')
        section12 = Page.objects.create(title='sub2', parent=section1, url='sub2')

    def get_non_staff_user(self):
        user = User.objects.create_user('user1', 'u@ser.nl', password="pass")
        user.is_staff = False
        return user

    def get_staff_user(self):
        user = User.objects.create_user('user2', 'u2@ser.nl', password="secure")
        user.is_staff = True
        return user

    def test_show_user_menu_all(self):
        # render menu with all pages
        t = Template("""
            {% load fiber_tags %}
            {% show_menu 'main' 1 999 "all" %}
            """
        )
        c = Context({
            'user': self.get_non_staff_user(),
            'fiber_page': Page.objects.get_by_url('/'),
        })
        with self.assertNumQueries(2):
            self.assertEquals(
                condense_html_whitespace(t.render(c)),
                ('<ul>'
                   '<li class="home first last">'
                     '<a href="/">home</a>'
                     '<ul>'
                       '<li class="section1 first">'
                         '<a href="/section1/">section1</a>'
                         '<ul>'
                           '<li class="sub1 first">'
                             '<a href="/section1/sub1/">sub1</a>'
                           '</li>'
                           '<li class="sub2 last">'
                             '<a href="/section1/sub2/">sub2</a>'
                           '</li>'
                         '</ul>'
                       '</li>'
                       '<li class="section2 last">'
                         '<a href="/section2/">section2</a>'
                       '</li>'
                     '</ul>'
                   '</li>'
                 '</ul>'))

    def test_show_user_menu_all_descendants(self):
        """
        Tests for 'all_descendants' with a minimum level
        """
        user = self.get_non_staff_user()

        t = Template("""
            {% load fiber_tags %}
            {% show_menu 'main' 2 999 "all_descendants" %}
            """
        )

        c = Context({
            'user': user,
            'fiber_page': Page.objects.get_by_url('/section1/'),
        })

        with self.assertNumQueries(2):
            self.assertEquals(
                condense_html_whitespace(t.render(c)),
                ('<ul>'
                   '<li class="section1 first">'
                     '<a href="/section1/">section1</a>'
                     '<ul>'
                       '<li class="sub1 first">'
                         '<a href="/section1/sub1/">sub1</a>'
                       '</li>'
                       '<li class="sub2 last">'
                         '<a href="/section1/sub2/">sub2</a>'
                       '</li>'
                     '</ul>'
                   '</li>'
                   '<li class="section2 last">'
                     '<a href="/section2/">section2</a>'
                   '</li>'
                 '</ul>'))

        c = Context({
            'user': user,
            'fiber_page': Page.objects.get_by_url('/section2/'),
        })

        with self.assertNumQueries(2):
            self.assertEquals(
                condense_html_whitespace(t.render(c)),
                ('<ul>'
                   '<li class="section1 first">'
                     '<a href="/section1/">section1</a>'
                   '</li>'
                   '<li class="section2 last">'
                     '<a href="/section2/">section2</a>'
                   '</li>'
                 '</ul>'))

    def test_show_user_menu_min_max_level(self):
        """
        Test for minimum and maximum level
        """
        t = Template("""
            {% load fiber_tags %}
            {% show_menu 'main' 2 2 %}
            """
        )
        c = Context({
            'user': self.get_non_staff_user(),
            'fiber_page': Page.objects.get_by_url('/section1/sub1/'),
        })
        with self.assertNumQueries(2):
            self.assertEquals(
                condense_html_whitespace(t.render(c)),
                ('<ul>'
                   '<li class="section1 first">'
                     '<a href="/section1/">section1</a>'
                   '</li>'
                   '<li class="section2 last">'
                     '<a href="/section2/">section2</a>'
                   '</li>'
                 '</ul>'))

        t = Template("""
            {% load fiber_tags %}
            {% show_menu 'main' 3 3 %}
            """
        )

        with self.assertNumQueries(2):
            self.assertEquals(
                condense_html_whitespace(t.render(c)),
                ('<ul>'
                   '<li class="sub1 first">'
                     '<a href="/section1/sub1/">sub1</a>'
                   '</li>'
                   '<li class="sub2 last">'
                     '<a href="/section1/sub2/">sub2</a>'
                   '</li>'
                 '</ul>'))

    def test_show_user_menu_different_root(self):
        """
        Test that show_menu only shows top level if current
        page is in different root.
        """
        other_root = Page.objects.create(title='other')

        t = Template("""
            {% load fiber_tags %}
            {% show_menu 'main' 1 999 %}
            """
        )
        c = Context({
            'user': self.get_non_staff_user(),
            'fiber_page': other_root,
        })
        with self.assertNumQueries(2):
            self.assertEquals(
                condense_html_whitespace(t.render(c)),
                ('<ul>'
                 '<li class="home first last">'
                 '<a href="/">home</a>'
                 '</li>'
                 '</ul>'))

    def test_show_admin_menu_all(self):
        # render menu with all pages
        t = Template("""
            {% load fiber_tags %}
            {% show_menu 'main' 1 999 "all" %}
            """
        )
        c = Context({
            'user': self.get_staff_user(),
            'fiber_page': Page.objects.get_by_url('/'),
        })

        with self.assertNumQueries(2):
            self.assertEquals(
                condense_html_whitespace(t.render(c)),
                ('<ul data-fiber-data=\'{ "type": "page", "add_url": "%(fiber_admin_page_add_url)s", "parent_id": 1 }\'>'
                   '<li class="home first last">'
                     '<a href="/" data-fiber-data=\'{ "can_edit": true, "type": "page", "id": 2, "parent_id": 1, "url": "%(fiber_admin_page_edit_url_home)s", "add_url": "%(fiber_admin_page_add_url)s" }\'>home</a>'
                     '<ul data-fiber-data=\'{ "type": "page", "add_url": "%(fiber_admin_page_add_url)s", "parent_id": 2 }\'>'
                       '<li class="section1 first">'
                         '<a href="/section1/" data-fiber-data=\'{ "can_edit": true, "type": "page", "id": 3, "parent_id": 2, "url": "%(fiber_admin_page_edit_url_section1)s", "add_url": "%(fiber_admin_page_add_url)s" }\'>section1</a>'
                         '<ul data-fiber-data=\'{ "type": "page", "add_url": "%(fiber_admin_page_add_url)s", "parent_id": 3 }\'>'
                           '<li class="sub1 first">'
                             '<a href="/section1/sub1/" data-fiber-data=\'{ "can_edit": true, "type": "page", "id": 5, "parent_id": 3, "url": "%(fiber_admin_page_edit_url_sub1)s", "add_url": "%(fiber_admin_page_add_url)s" }\'>sub1</a>'
                           '</li>'
                           '<li class="sub2 last">'
                             '<a href="/section1/sub2/" data-fiber-data=\'{ "can_edit": true, "type": "page", "id": 6, "parent_id": 3, "url": "%(fiber_admin_page_edit_url_sub2)s", "add_url": "%(fiber_admin_page_add_url)s" }\'>sub2</a>'
                           '</li>'
                         '</ul>'
                       '</li>'
                       '<li class="section2 last">'
                         '<a href="/section2/" data-fiber-data=\'{ "can_edit": true, "type": "page", "id": 4, "parent_id": 2, "url": "%(fiber_admin_page_edit_url_section2)s", "add_url": "%(fiber_admin_page_add_url)s" }\'>section2</a>'
                       '</li>'
                     '</ul>'
                   '</li>'
                 '</ul>' % {
                        'fiber_admin_page_add_url': reverse('fiber_admin:fiber_page_add'),
                        'fiber_admin_page_edit_url_home': reverse('fiber_admin:fiber_page_change', args=(2, )),
                        'fiber_admin_page_edit_url_section1': reverse('fiber_admin:fiber_page_change', args=(3, )),
                        'fiber_admin_page_edit_url_section2': reverse('fiber_admin:fiber_page_change', args=(4, )),
                        'fiber_admin_page_edit_url_sub1': reverse('fiber_admin:fiber_page_change', args=(5, )),
                        'fiber_admin_page_edit_url_sub2': reverse('fiber_admin:fiber_page_change', args=(6, )),
                        }
                 ))


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
