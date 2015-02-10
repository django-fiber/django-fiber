import json
import time
from datetime import datetime
from mock import patch

from django.conf.urls import patterns, url
from django.views.generic import View
from django.core.urlresolvers import reverse
from django.template import Template, Context
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User

from fiber.utils.validators import FiberURLValidator
from fiber.mixins import FiberPageMixin
from fiber.sitemaps import FiberSitemap
from fiber.models import Page, ContentItem, PageContentItem
from fiber.utils import date
from ..test_util import get_short_django_version, format_list, condense_html_whitespace

try:
    from django.utils.timezone import make_aware, utc
except ImportError:
    pass


class ContentItemTest(TestCase):

    def generate_data(self):
        """
        Generate test data:
         - page1, page2, page3
         - content a: on page 1 and 2
         - content b: on page 3
         - content c: unused
        """
        page1 = Page.objects.create(title='page1')
        page2 = Page.objects.create(title='page2')
        page3 = Page.objects.create(title='page2')

        content_a = ContentItem.objects.create(name='a')
        content_b = ContentItem.objects.create(name='b')
        content_c = ContentItem.objects.create(name='c')

        PageContentItem.objects.create(page=page1, content_item=content_a)
        PageContentItem.objects.create(page=page2, content_item=content_a)
        PageContentItem.objects.create(page=page3, content_item=content_b)

    def test_get_content_groups(self):
        self.generate_data()

        content_groups = ContentItem.objects.get_content_groups()

        self.assertEquals(
            format_list([g['label'] for g in content_groups], must_sort=False, separator=';'),
            'used more than once;unused;used once;recently changed'
        )
        self.assertEquals(
            format_list(n['label'] for n in content_groups[0]['children']),
            'a'
        )
        self.assertEquals(
            format_list(n['label'] for n in content_groups[1]['children']),
            'c'
        )
        self.assertEquals(
            format_list(n['label'] for n in content_groups[2]['children']),
            'b'
        )
        self.assertEquals(
            format_list(n['label'] for n in content_groups[3]['children']),
            'a b c'
        )

    def test_rename_url(self):

        def check_content(name, html):
            self.assertEquals(
                condense_html_whitespace(
                    ContentItem.objects.get(name=name).content_html
                ),
                html
            )

        # generate data
        ContentItem.objects.create(
            name='a',
            content_html='<p>p</p><p><a href="/section1/">1</a></p>',
            content_markup='p. p\n\n"1":/section1/'
        )
        ContentItem.objects.create(
            name='b',
            content_html='<p><a href="/section1/abc/">abc</a></p>',
            content_markup='"abc":/section1/abc/'
        )
        ContentItem.objects.create(
            name='c',
            content_html='<p><a href="/section2/">2</a></p>',
            content_markup='"2":/section2/'
        )

        # rename url 'section1' to 'main'
        ContentItem.objects.rename_url('/section1/', '/main/')

        check_content('a', '<p>p</p><p><a href="/main/">1</a></p>')
        check_content('b', '<p><a href="/main/abc/">abc</a></p>')
        check_content('c', '<p><a href="/section2/">2</a></p>')


class PageTest(TestCase):

    def generate_data(self):
        """
        ---home
        ------section1 (/section1/)
        ---------abc (/section1/abc/)
        ------------xyz (/section1/abc/xyz/)
        ------section2 (/section2/)
        ---------def (/def/)  # absolute url
        ---------ghi (/section2/ghi/)
        """
        page_home_id = Page.objects.create(title='home').id
        page_section1_id = Page.objects.create(title='section1', parent_id=page_home_id, url='section1').id
        page_section2_id = Page.objects.create(title='section2', parent_id=page_home_id, url='section2').id
        page_abc_id = Page.objects.create(title='abc', parent_id=page_section1_id, url='abc').id
        Page.objects.create(title='xyz', parent_id=page_abc_id, url='xyz')
        page_def_id = Page.objects.create(title='def', parent_id=page_section2_id, url='/def/').id  # absolute url
        page_ghi_id = Page.objects.create(title='ghi', parent_id=page_section2_id, url='ghi').id
        Page.objects.create(title='example', url='http://example.com')

        page_def = Page.objects.get(id=page_def_id)
        page_ghi = Page.objects.get(id=page_ghi_id)
        page_ghi.move_to(page_def, 'right')

    def test_move_page(self):
        # generate data
        self.generate_data()

        ContentItem.objects.create(
            name='a',
            content_markup='"abc":/section1/abc/',
            content_html='<p><a href="/section1/abc/">abc</a></p>'
        )
        ContentItem.objects.create(
            name='b',
            content_markup='"xyz":/section1/abc/xyz/',
            content_html='<p><a href="/section1/abc/xyz/">xyz</a></p>'
        )

        # move 'abc' to 'section2', as first child
        page_section2 = Page.objects.get(title='section2')
        page_abc = Page.objects.get(title='abc')

        page_abc.move_page(page_section2.id, 'inside')

        page_abc = Page.objects.get(title='abc')  # reload the page
        self.assertEquals(page_abc.parent.title, 'section2')
        self.assertEquals(page_abc.get_previous_sibling(), None)
        self.assertEquals(page_abc.get_next_sibling().title, 'def')

        # references in content items are changed
        self.assertEquals(
            condense_html_whitespace(
                ContentItem.objects.get(name='a').content_html
            ),
            '<p><a href="/section2/abc/">abc</a></p>'
        )
        self.assertEquals(
            condense_html_whitespace(
                ContentItem.objects.get(name='b').content_html
            ),
            '<p><a href="/section2/abc/xyz/">xyz</a></p>'
        )

        # move 'xyz' to 'section2', to the right of 'def'
        page_xyz = Page.objects.get(title='xyz')
        page_def = Page.objects.get(title='def')
        page_section2 = Page.objects.get(title='section2')

        page_xyz.move_page(page_def.id, 'after')

        page_xyz = Page.objects.get(title='xyz')  # reload the page
        self.assertEquals(page_xyz.parent.title, 'section2')
        self.assertEquals(page_xyz.get_previous_sibling().title, 'def')
        self.assertEquals(page_xyz.get_next_sibling().title, 'ghi')

    def test_get_absolute_url(self):

        def test_url(title, url):
            self.assertEquals(
                Page.objects.get(title=title).get_absolute_url(),
                url
            )

        # generate data
        self.generate_data()

        # test urls
        test_url('home', '')
        test_url('section1', '/section1/')
        test_url('abc', '/section1/abc/')
        test_url('def', '/def/')
        test_url('example', 'http://example.com')

    def test_change_relative_url(self):
        # generate data
        self.generate_data()

        ContentItem.objects.create(
            name='a',
            content_markup='"abc":/section1/abc/',
            content_html='<p><a href="/section1/abc/">abc</a></p>'
        )
        ContentItem.objects.create(
            name='b',
            content_markup='"xyz":/section1/abc/xyz/',
            content_html='<p><a href="/section1/abc/xyz/">xyz</a></p>'
        )

        # change relative url of page 'abc'
        page_abc = Page.objects.get(title='abc')
        page_abc.url = 'a_b_c'
        page_abc.save()

        # references in content items are changed
        self.assertEquals(
            condense_html_whitespace(
                ContentItem.objects.get(name='a').content_html
            ),
            '<p><a href="/section1/a_b_c/">abc</a></p>'
        )
        self.assertEquals(
            condense_html_whitespace(
                ContentItem.objects.get(name='b').content_html
            ),
            '<p><a href="/section1/a_b_c/xyz/">xyz</a></p>'
        )

    def test_unicode(self):
        self.assertEqual(unicode(Page(title='abc')), 'abc')

    def test_is_first_child(self):
        # setup
        self.generate_data()

        # root page
        self.assertTrue(Page.objects.get(title='home').is_first_child())

        # first child
        self.assertTrue(Page.objects.get(title='section1').is_first_child())

        # second child
        self.assertFalse(Page.objects.get(title='section2').is_first_child())

    def test_is_is_last_child(self):
        # setup
        self.generate_data()

        # root page
        self.assertTrue(Page.objects.get(title='home').is_last_child())

        # first child
        self.assertFalse(Page.objects.get(title='section1').is_last_child())

        # last child
        self.assertTrue(Page.objects.get(title='section2').is_last_child())

    def test_get_ancestors(self):
        # setup
        self.generate_data()
        page_def = Page.objects.get(title='def')

        # - get ancestors
        self.assertEqual(format_list(page_def.get_ancestors()), 'home section2')

        # - call again; expect 0 queries
        self.assertNumQueries(0, lambda: page_def.get_ancestors())


class PageContentItemTest(TestCase):

    def test_move(self):

        def get_content(page_id, block_name='main'):
            page = Page.objects.get(id=page_id)
            return format_list(
                [i.content_item.name for i in page.get_content_for_block(block_name).order_by('sort')],
                must_sort=False
            )

        # generate data
        content_a = ContentItem.objects.create(name='a')
        content_b = ContentItem.objects.create(name='b')
        content_c = ContentItem.objects.create(name='c')

        page = Page.objects.create(title='page')
        item_a = PageContentItem.objects.create(page=page, content_item=content_a, block_name='main', sort=0)
        item_b = PageContentItem.objects.create(page=page, content_item=content_b, block_name='main', sort=1)
        item_c = PageContentItem.objects.create(page=page, content_item=content_c, block_name='main', sort=2)

        # 1. get content
        self.assertEquals(u'a b c', get_content(page.id))

        # 2. move 'a' before 'c'
        item_a.move(item_c.id)

        self.assertEquals(u'b a c', get_content(page.id))

        # 3. move 'c' before 'a'
        item_c.move(item_a.id)
        self.assertEquals(u'b c a', get_content(page.id))

        # 4. move 'b' last
        item_b.move()
        self.assertEquals(u'c a b', get_content(page.id))

        # 5. move 'a' to block 'side'
        item_a.move(block_name='side')
        self.assertEquals(u'c b', get_content(page.id, 'main'))
        self.assertEquals(u'a', get_content(page.id, 'side'))

        # 6. move 'c' before 'a' in block 'side'
        item_a = PageContentItem.objects.get(id=item_a.id)
        item_c = PageContentItem.objects.get(id=item_c.id)

        item_c.move(item_a.id, block_name='side')
        self.assertEquals(u'b', get_content(page.id, 'main'))
        self.assertEquals(u'c a', get_content(page.id, 'side'))


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


class TestView(View):
    pass


urlpatterns = patterns('',
    url(r'^test_url/$', TestView.as_view(), name='another_named_url'),
)


class TestUtilsURLValidator(TestCase):
    urls = urlpatterns  # use this url conf for our tests
    validator = FiberURLValidator()

    def test_passes_normal(self):
        self.assertEqual(self.validator('http://www.google.com/'), None)

    def test_passes_url_contains_anchor(self):
        self.assertEqual(self.validator('/some/page/#SomeAnchor'), None)

    def test_passes_url_contains_querystring_and_anchor(self):
        self.assertEqual(self.validator('/some/page/?id=12&user_id=1#SomeAnchor'), None)

    def test_named_url(self):
        # Must raise if named url does not exist
        with self.assertRaises(ValidationError):
            self.validator('"some_named_url"')

        # Named url does exist
        self.assertEquals(self.validator('"another_named_url"'), None)

        # A fiber page also uses that named_url
        Page.objects.create(title='some_page', url='"another_named_url"').save()
        self.assertEquals(self.validator('"another_named_url"'), None)


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


class TestContentItem(TestCase):
    def test_unicode(self):
        # with name
        self.assertEqual(unicode(ContentItem(name='abc')), 'abc')

        # without name, no content
        self.assertEqual(unicode(ContentItem()), '[ EMPTY ]')

        # without name, content length < 50
        self.assertEqual(unicode(ContentItem(content_html='xyz')), 'xyz')

        # without name, content length > 50
        self.assertEqual(unicode(ContentItem(content_html='abcdefghij' * 6)), 'abcdefghijabcdefghijabcdefghijabcdefghijabcdefghij...')

    def test_get_add_url(self):
        self.assertEqual(ContentItem.get_add_url(), '/admin/fiber/fiber_admin/fiber/contentitem/add/')

    def test_get_change_url(self):
        content_item1 = ContentItem.objects.create()

        self.assertEqual(content_item1.get_change_url(), '/admin/fiber/fiber_admin/fiber/contentitem/%d/' % content_item1.id)

    def test_used_on_pages_json(self):
        # setup
        page1 = Page.objects.create(title='p1', url='/abc/')
        content_item1 = ContentItem.objects.create()
        PageContentItem.objects.create(page=page1, content_item=content_item1)

        # - call get_used_on_pages_json
        self.assertEqual(
            json.loads(
                content_item1.get_used_on_pages_json()
            ),
            [
                {"url": "/abc/", "title": "p1"}
            ]
        )

        # - load contentitem
        content_item1 = ContentItem.objects.get(id=content_item1.id)
        self.assertEqual(content_item1.used_on_pages_data, [dict(url='/abc/', title='p1')])

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



def mock_tz_now():
    """
    Return january 15 2013 10:30

    Depending on the Django version and the settings it will return a datetime with or without timezone.
    """
    result = datetime(2013, 1, 15, 10, 30)

    if get_short_django_version() >= (1, 4) and settings.USE_TZ:
        return make_aware(result, utc)
    else:
        return result


class FiberTests(TestCase):
    def test_fiber(self):
        # setup
        frontpage = Page.objects.create(title='frontpage', url='/')
        lorem_ipsum = ContentItem.objects.create(content_html='lorem ipsum')
        PageContentItem.objects.create(page=frontpage, content_item=lorem_ipsum, block_name='main')

        # - get page
        response = self.client.get('/')
        self.assertContains(response, 'lorem ipsum')

    @patch('fiber.utils.date.tz_now', mock_tz_now)
    def test_friendly_datetime(self):
        self.assertEqual(date.friendly_datetime(datetime(2013, 1, 15, 10, 30)), 'just now')
        self.assertEqual(date.friendly_datetime(datetime(2013, 1, 15, 10, 29, 40)), '20 seconds ago')
        self.assertEqual(date.friendly_datetime(datetime(2013, 1, 15, 10, 29)), 'a minute ago')
        self.assertEqual(date.friendly_datetime(datetime(2013, 1, 15, 10, 25)), '5 minutes ago')
        self.assertEqual(date.friendly_datetime(datetime(2013, 1, 15, 9, 30)), 'an hour ago')
        self.assertEqual(date.friendly_datetime(datetime(2013, 1, 15, 8)), '2 hours ago')
        self.assertEqual(date.friendly_datetime(datetime(2013, 1, 14, 7)), 'yesterday')
        self.assertEqual(date.friendly_datetime(datetime(2013, 1, 13)), '2 days ago')
        self.assertEqual(date.friendly_datetime(datetime(2013, 1, 8)), 'a week ago')
        self.assertEqual(date.friendly_datetime(datetime(2013, 1, 1)), '2 weeks ago')
        self.assertEqual(date.friendly_datetime(datetime(2012, 12, 1)), '1 months ago')
        self.assertEqual(date.friendly_datetime(datetime(2012, 11, 1)), '2 months ago')
        self.assertEqual(date.friendly_datetime(datetime(2012, 1, 1)), '1 years ago')

        # in the future
        self.assertEqual(date.friendly_datetime(datetime(2013, 2, 1)), '')

        # invalid input
        self.assertEqual(date.friendly_datetime('abc'), 'abc')

        # timestamp
        self.assertEqual(
            date.friendly_datetime(
                int(time.mktime(datetime(2013, 1, 15, 10, 29, 20).timetuple()))
            ),
            '40 seconds ago'
        )

    def test_page_view(self):
        # setup
        p1 = Page.objects.create(title='p1', url='/p1/')
        Page.objects.create(title='p2', url='/p2', template_name='template1.html')
        Page.objects.create(title='p3', url='/p3', is_public=False)
        Page.objects.create(title='p4', url='/p4', redirect_page=p1)

        # page with default template
        self.assertContains(self.client.get('/p1/'), '<title>p1</title>')

        # page with custom template
        self.assertContains(self.client.get('/p2'), 'This is template1.')

        # url without trailing '/'
        response = self.client.get('/p1')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], 'http://testserver/p1/')

        # url does not exist
        self.assertEqual(self.client.get('/xyz/').status_code, 404)

        # private page
        self.assertEqual(self.client.get('/p3').status_code, 404)

        # redirect page
        response = self.client.get('/p4')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], 'http://testserver/p1/')

    def test_admin(self):
        # setup
        lorem_ipsum = ContentItem.objects.create(content_html='lorem ipsum')

        User.objects.create_superuser('admin', 'admin@ridethepony.nl', 'admin')

        self.client.login(username='admin', password='admin')

        # get admin page for content item
        self.client.get('/admin/fiber/contentitem/%d/' % lorem_ipsum.id)
