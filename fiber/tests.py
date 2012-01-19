from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template import Template, Context
from django.test import TestCase

from models import ContentItem, Page, PageContentItem


def format_list(l, must_sort=True, separator=' '):
    """
    Format a list as a string. Default the items in the list are sorted.
    E.g.
    >>> format_list([3, 2, 1])
    u'1 2 3'
    """
    titles = [unicode(v) for v in l]
    if must_sort:
        titles = sorted(titles)

    return separator.join(titles)


def strip_whitespace(text):
    return text.replace(
        '\n', ''
    ).replace(
        '\t', ''
    ).strip()


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
            format_list([g['title'] for g in content_groups], must_sort=False, separator=';'),
            'used more than once;unused;used once;recently changed'
        )
        self.assertEquals(
            format_list(content_groups[0]['content_items']),
            'a'
        )
        self.assertEquals(
            format_list(content_groups[1]['content_items']),
            'c'
        )
        self.assertEquals(
            format_list(content_groups[2]['content_items']),
            'b'
        )
        self.assertEquals(
            format_list(content_groups[3]['content_items']),
            'a b c'
        )

    def test_rename_url(self):

        def check_content(name, html):
            self.assertEquals(
                strip_whitespace(
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

        page_abc.move_page(page_section2.id)

        page_abc = Page.objects.get(title='abc')  # reload the page
        self.assertEquals(page_abc.parent.title, 'section2')
        self.assertEquals(page_abc.get_previous_sibling(), None)
        self.assertEquals(page_abc.get_next_sibling().title, 'def')

        # references in content items are changed
        self.assertEquals(
            strip_whitespace(
                ContentItem.objects.get(name='a').content_html
            ),
            '<p><a href="/section2/abc/">abc</a></p>'
        )
        self.assertEquals(
            strip_whitespace(
                ContentItem.objects.get(name='b').content_html
            ),
            '<p><a href="/section2/abc/xyz/">xyz</a></p>'
        )

        # move 'xyz' to 'section2', to the right of 'def'
        page_xyz = Page.objects.get(title='xyz')
        page_def = Page.objects.get(title='def')
        page_section2 = Page.objects.get(title='section2')

        page_xyz.move_page(page_section2.id, page_def.id)

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
            strip_whitespace(
                ContentItem.objects.get(name='a').content_html
            ),
            '<p><a href="/section1/a_b_c/">abc</a></p>'
        )
        self.assertEquals(
            strip_whitespace(
                ContentItem.objects.get(name='b').content_html
            ),
            '<p><a href="/section1/a_b_c/xyz/">xyz</a></p>'
        )


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
        PageContentItem.objects.move(item_a, item_c)

        self.assertEquals(u'b a c', get_content(page.id))

        # 3. move 'c' before 'a'
        PageContentItem.objects.move(item_c, item_a)
        self.assertEquals(u'b c a', get_content(page.id))

        # 4. move 'b' last
        PageContentItem.objects.move(item_b, None)
        self.assertEquals(u'c a b', get_content(page.id))

        # 5. move 'a' to block 'side'
        PageContentItem.objects.move(item_a, block_name='side')
        self.assertEquals(u'c b', get_content(page.id, 'main'))
        self.assertEquals(u'a', get_content(page.id, 'side'))

        # 6. move 'c' before 'a' in block 'side'
        item_a = PageContentItem.objects.get(id=item_a.id)
        item_c = PageContentItem.objects.get(id=item_c.id)

        PageContentItem.objects.move(item_c, item_a, block_name='side')
        self.assertEquals(u'b', get_content(page.id, 'main'))
        self.assertEquals(u'c a', get_content(page.id, 'side'))


class TestTemplateTags(TestCase):

    def generate_data(self):
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
        self.generate_data()

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
                strip_whitespace(t.render(c)),
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
        self.generate_data()
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
                strip_whitespace(t.render(c)),
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
                strip_whitespace(t.render(c)),
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
        self.generate_data()

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
                strip_whitespace(t.render(c)),
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
                strip_whitespace(t.render(c)),
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
        self.generate_data()
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
                strip_whitespace(t.render(c)),
                ('<ul>'
                 '<li class="home first last">'
                 '<a href="/">home</a>'
                 '</li>'
                 '</ul>'))


    def test_show_admin_menu_all(self):
        self.generate_data()

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
                strip_whitespace(t.render(c)),
                ('<ul data-fiber-data=\'{"type": "page", "add_url": "%(fiber_admin_page_add_url)s", "parent_id": 1}\'>'
                   '<li class="home first last">'
                     '<a href="/" data-fiber-data=\'{"type": "page", "id": 2, "parent_id": 1, "url": "%(fiber_admin_page_edit_url_home)s", "add_url": "%(fiber_admin_page_add_url)s"}\'>home</a>'
                     '<ul data-fiber-data=\'{"type": "page", "add_url": "%(fiber_admin_page_add_url)s", "parent_id": 2}\'>'
                       '<li class="section1 first">'
                         '<a href="/section1/" data-fiber-data=\'{"type": "page", "id": 3, "parent_id": 2, "url": "%(fiber_admin_page_edit_url_section1)s", "add_url": "%(fiber_admin_page_add_url)s"}\'>section1</a>'
                         '<ul data-fiber-data=\'{"type": "page", "add_url": "%(fiber_admin_page_add_url)s", "parent_id": 3}\'>'
                           '<li class="sub1 first">'
                             '<a href="/section1/sub1/" data-fiber-data=\'{"type": "page", "id": 5, "parent_id": 3, "url": "%(fiber_admin_page_edit_url_sub1)s", "add_url": "%(fiber_admin_page_add_url)s"}\'>sub1</a>'
                           '</li>'
                           '<li class="sub2 last">'
                             '<a href="/section1/sub2/" data-fiber-data=\'{"type": "page", "id": 6, "parent_id": 3, "url": "%(fiber_admin_page_edit_url_sub2)s", "add_url": "%(fiber_admin_page_add_url)s"}\'>sub2</a>'
                           '</li>'
                         '</ul>'
                       '</li>'
                       '<li class="section2 last">'
                         '<a href="/section2/" data-fiber-data=\'{"type": "page", "id": 4, "parent_id": 2, "url": "%(fiber_admin_page_edit_url_section2)s", "add_url": "%(fiber_admin_page_add_url)s"}\'>section2</a>'
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
