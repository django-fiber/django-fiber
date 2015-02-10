from django.core.urlresolvers import reverse
from django.template import Template, Context
from django.test import TestCase
from django.contrib.auth.models import User

from fiber.models import Page, ContentItem, PageContentItem
from ..test_util import condense_html_whitespace


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

    def test_show_page_content(self):
        # The show_page_content templatetag should support rendering content from multiple pages in one view.

        p1 = Page.objects.create(title='p1')
        c1 = ContentItem.objects.create(content_html='<p>c1</p>')
        PageContentItem.objects.create(content_item=c1, page=p1, block_name='test_block')
        p2 = Page.objects.create(title='p2')
        c2 = ContentItem.objects.create(content_html='<p>c2</p>')
        PageContentItem.objects.create(content_item=c2, page=p2, block_name='test_block')

        t = Template("""
            {% load fiber_tags %}
            {% show_page_content second_page 'test_block' %}
            {% show_page_content 'test_block' %}
            """
            )

        c = Context({
            'fiber_page': p1,
            'second_page': p2
        })

        self.assertEquals(
            condense_html_whitespace(t.render(c)),
            ('<div><div class="content"><p>c2</p></div></div><div><div class="content"><p>c1</p></div></div>'))
