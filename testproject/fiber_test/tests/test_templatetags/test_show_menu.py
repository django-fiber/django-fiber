from django.template import Template, Context
from django.test import TestCase
from django.contrib.auth.models import User, AnonymousUser
from django.urls import reverse

from fiber.models import Page
from ...test_util import RenderMixin


class BaseTestShowMenu(RenderMixin, TestCase):
    def setUp(self):
        # Create the page/menu tree (based on the docs):
        #
        # - main
        #   - Home (hidden!)
        #   - About
        #     - Mission
        #     - People
        #   - News
        #   - Products
        #     - Product A
        #       - Testimonials
        #       - Downloads
        #         - Data sheet
        #         - Manual
        #     - Product B
        #       - Downloads
        #     - Product C (hidden!)
        #       - Downloads
        #   - Contact
        #     - Newsletter
        #     - Directions
        # - general
        #   - Disclaimer
        #   - Privacy

        # Mainmenu
        self.main = Page.objects.create(title='main')

        # Home
        self.home = Page.objects.create(title='home', parent=self.main, url='/', is_public=False)

        # About section
        self.about = Page.objects.create(title='about', parent=self.main, url='about')
        self.mission = Page.objects.create(title='mission', parent=self.about, url='mission')
        Page.objects.create(title='people', parent=self.about, url='people')

        # News
        self.news = Page.objects.create(title='news', parent=self.main, url='news')

        # Products section
        self.products = Page.objects.create(title='products', parent=self.main, url='products')
        #   - Product A
        self.product_a = Page.objects.create(title='product a', parent=self.products, url='product-a')
        Page.objects.create(title='testimonials', parent=self.product_a, url='testimonials')
        self.downloads = Page.objects.create(title='downloads', parent=self.product_a, url='downloads')
        Page.objects.create(title='data sheet', parent=self.downloads, url='data-sheet')
        self.manual = Page.objects.create(title='manual', parent=self.downloads, url='manual')
        #   - Product B
        product_b = Page.objects.create(title='product b', parent=self.products, url='product-b')
        Page.objects.create(title='downloads', parent=product_b, url='downloads')
        #   - Product C
        self.product_c = Page.objects.create(title='product c', parent=self.products, url='product-c', is_public=False)
        Page.objects.create(title='downloads', parent=self.product_c, url='downloads')

        # Contact section
        self.contact = Page.objects.create(title='contact', parent=self.main, url='contact')
        Page.objects.create(title='newsletter', parent=self.contact, url='newsletter')
        Page.objects.create(title='directions', parent=self.contact, url='directions')

        # General menu
        general = Page.objects.create(title='general')
        self.disclaimer = Page.objects.create(title='disclaimer', parent=general, url='disclaimer')
        Page.objects.create(title='privacy', parent=general, url='privacy')

        # User
        self.anon = AnonymousUser()


class TestShowMenu(BaseTestShowMenu):
    """
    Show first and second level pages, below the root menu named 'main'
    """

    def test_show_menu_main_1_2_on_home(self):
        """
        When visiting the 'home' page, this will only show the first level items
        """
        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 1 2 %}',
                '''
                <ul>
                    <li class="about"><a href="/about/">about</a></li>
                    <li class="news"><a href="/news/">news</a></li>
                    <li class="products"><a href="/products/">products</a></li>
                    <li class="contact last"><a href="/contact/">contact</a></li>
                </ul>''', {
                    'user': self.anon,
                    'fiber_page': self.home
                })

    def test_show_menu_main_1_2_on_products(self):
        """
        When visiting the 'products' page, this will expand the sub pages of the active page.
        """
        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 1 2 %}',
                '''
                <ul>
                    <li class="about"><a href="/about/">about</a></li>
                    <li class="news"><a href="/news/">news</a></li>
                    <li class="products">
                        <a href="/products/">products</a>
                        <ul>
                            <li class="product-a first"><a href="/products/product-a/">product a</a></li>
                            <li class="product-b"><a href="/products/product-b/">product b</a></li>
                        </ul>
                    </li>
                    <li class="contact last"><a href="/contact/">contact</a></li>
                </ul>''', {
                    'user': self.anon,
                    'fiber_page': self.products
                })

    def test_show_menu_main_1_2_on_product_a(self):
        """
        When visiting the 'product a' page, this will expand the sub pages of the active page.

        The sub pages of 'product a' are NOT shown, because they are outside of the specified maximum level.
        """
        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 1 2 %}',
                '''
                <ul>
                    <li class="about"><a href="/about/">about</a></li>
                    <li class="news"><a href="/news/">news</a></li>
                    <li class="products">
                        <a href="/products/">products</a>
                        <ul>
                            <li class="product-a first"><a href="/products/product-a/">product a</a></li>
                            <li class="product-b"><a href="/products/product-b/">product b</a></li>
                        </ul>
                    </li>
                    <li class="contact last"><a href="/contact/">contact</a></li>
                </ul>''', {
                    'user': self.anon,
                    'fiber_page': self.product_a
                })

    def test_show_menu_main_1_2_on_disclaimer(self):
        """
        When visiting the 'disclaimer' page, this will only show the first level items
        """
        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 1 2 %}',
                '''
                <ul>
                    <li class="about"><a href="/about/">about</a></li>
                    <li class="news"><a href="/news/">news</a></li>
                    <li class="products"><a href="/products/">products</a></li>
                    <li class="contact last"><a href="/contact/">contact</a></li>
                </ul>''', {
                    'user': self.anon,
                    'fiber_page': self.disclaimer
                })

    def test_show_menu_main_1_2_on_non_fiber_page(self):
        """
        When visiting the a non-fiber page, this will only show the first level items
        """
        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 1 2 %}',
                '''
                <ul>
                    <li class="about"><a href="/about/">about</a></li>
                    <li class="news"><a href="/news/">news</a></li>
                    <li class="products"><a href="/products/">products</a></li>
                    <li class="contact last"><a href="/contact/">contact</a></li>
                </ul>''', {
                    'user': self.anon
                })


class TestShowSubMenu(BaseTestShowMenu):
    menu_2_2 = '''
    <ul>
        <li class="product-a first"><a href="/products/product-a/">product a</a></li>
        <li class="product-b"><a href="/products/product-b/">product b</a></li>
    </ul>'''
    menu_3_3 = '''
    <ul>
        <li class="testimonials first"><a href="/products/product-a/testimonials/">testimonials</a></li>
        <li class="downloads last"><a href="/products/product-a/downloads/">downloads</a></li>
    </ul>'''

    def test_show_menu_main_2_2_on_product_a(self):
        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 2 2 %}',
                self.menu_2_2, {
                    'user': self.anon,
                    'fiber_page': self.product_a
                })

    def test_show_menu_main_2_2_on_product_a_downloads(self):
        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 2 2 %}',
                self.menu_2_2, {
                    'user': self.anon,
                    'fiber_page': self.downloads
                })

    def test_show_menu_main_2_2_on_product_c(self):
        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 2 2 %}',
                self.menu_2_2, {
                    'user': self.anon,
                    'fiber_page': self.product_c
                })

    def test_show_menu_main_2_2_on_home(self):
        """
        When visiting the 'home' page, this will show an empty menu, since no level 3 pages are currently active.
        """
        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 2 2 %}',
                '<ul></ul>', {
                    'user': self.anon,
                    'fiber_page': self.home
                })

    def test_show_menu_main_3_3_on_product_a(self):
        """When visiting the 'product_a' page the subpages are visible"""
        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 3 3 %}',
                self.menu_3_3, {
                    'user': self.anon,
                    'fiber_page': self.product_a
                })

    def test_show_menu_main_3_3_on_product_a_downloads(self):
        """When visiting the 'downloads' page the siblings are visible"""
        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 3 3 %}',
                self.menu_3_3, {
                    'user': self.anon,
                    'fiber_page': self.downloads
                })

    def test_show_menu_main_3_3_on_product_c(self):
        """When visiting the (hidden) 'product_c' page the subpage is visible"""
        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 3 3 %}',
                '''
                <ul>
                    <li class="downloads first last"><a href="/products/product-c/downloads/">downloads</a></li>
                </ul>''', {
                    'user': self.anon,
                    'fiber_page': self.product_c
                })

    def test_show_menu_main_3_3_on_home(self):
        """
        When visiting the 'home' page, this will show an empty menu, since no level 3 pages are currently active.
        """
        with self.assertNumQueries(1):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 3 3 %}',
                '<ul></ul>', {
                    'user': self.anon,
                    'fiber_page': self.home
                })

    def test_show_menu_main_3_5_on_product_a(self):
        """When visiting the 'product_a' page the subpages are visible"""
        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 3 5 %}',
                '''
                <ul>
                    <li class="testimonials first"><a href="/products/product-a/testimonials/">testimonials</a></li>
                    <li class="downloads last"><a href="/products/product-a/downloads/">downloads</a></li>
                </ul>''', {
                    'user': self.anon,
                    'fiber_page': self.product_a
                })

    def test_show_menu_main_3_5_on_product_a_downloads(self):
        """When visiting the 'downloads' page the subpages and siblings are visible"""
        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 3 5 %}',
                '''
                <ul>
                    <li class="testimonials first"><a href="/products/product-a/testimonials/">testimonials</a></li>
                    <li class="downloads last">
                        <a href="/products/product-a/downloads/">downloads</a>
                        <ul>
                            <li class="data-sheet first"><a href="/products/product-a/downloads/data-sheet/">data sheet</a></li>
                            <li class="manual last"><a href="/products/product-a/downloads/manual/">manual</a></li>
                        </ul>
                    </li>
                </ul>
                ''', {
                    'user': self.anon,
                    'fiber_page': self.downloads
                })

    def test_show_menu_main_3_5_on_product_a_downloads_manual(self):
        """When visiting the 'manual' page the subpages and siblings are visible"""
        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 3 5 %}',
                '''
                <ul>
                    <li class="testimonials first"><a href="/products/product-a/testimonials/">testimonials</a></li>
                    <li class="downloads last">
                        <a href="/products/product-a/downloads/">downloads</a>
                        <ul>
                            <li class="data-sheet first"><a href="/products/product-a/downloads/data-sheet/">data sheet</a></li>
                            <li class="manual last"><a href="/products/product-a/downloads/manual/">manual</a></li>
                        </ul>
                    </li>
                </ul>
                ''', {
                    'user': self.anon,
                    'fiber_page': self.manual
                })

    def test_show_menu_main_3_5_on_product_c(self):
        """When visiting the (hidden) 'product_c' page the subpage is visible"""
        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 3 5 %}',
                '''
                <ul>
                    <li class="downloads first last"><a href="/products/product-c/downloads/">downloads</a></li>
                </ul>''', {
                    'user': self.anon,
                    'fiber_page': self.product_c
                })


class TestShowSubMenuAllDescendants(BaseTestShowMenu):
    """
    Show pages from level 3 to 5, in the menu 'main', also show all descendants of the currently active page.
    """
    menu_3_5 = '''
    <ul>
        <li class="testimonials first"><a href="/products/product-a/testimonials/">testimonials</a></li>
        <li class="downloads last">
            <a href="/products/product-a/downloads/">downloads</a>
            <ul>
                <li class="data-sheet first"><a href="/products/product-a/downloads/data-sheet/">data sheet</a></li>
                <li class="manual last"><a href="/products/product-a/downloads/manual/">manual</a></li>
            </ul>
        </li>
    </ul>'''

    def test_show_menu_main_3_5_all_descendants_on_non_fiber(self):
        """
        When visiting the a non-fiber page, this will show an empty menu, since no level 3 pages are currently active.
        """
        with self.assertNumQueries(1):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 3 5 "all_descendants" %}',
                '<ul></ul>', {
                    'user': self.anon
                })

    def test_show_menu_main_3_5_all_descendants_on_product_a(self):
        """
        When visiting the 'product a' page all descendants and their siblings of the 'product a' page are visible.
        """
        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 3 5 "all_descendants" %}',
                self.menu_3_5, {
                    'user': self.anon,
                    'fiber_page': self.product_a
                })

    def test_show_menu_main_3_5_all_descendants_on_downloads(self):
        """
        When visiting the 'downloads' page all descendants and their siblings of the 'product a' page are visible.
        """
        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 3 5 "all_descendants" %}',
                self.menu_3_5, {
                    'user': self.anon,
                    'fiber_page': self.downloads
                })

    def test_show_menu_main_3_5_all_descendants_on_manual(self):
        """
        When visiting the 'manual' page all descendants and their siblings of the 'product a' page are visible.
        """
        with self.assertNumQueries(2):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 3 5 "all_descendants" %}',
                self.menu_3_5, {
                    'user': self.anon,
                    'fiber_page': self.manual
                })

    def test_show_menu_main_3_5_all_descendants_on_home(self):
        """
        When visiting the 'home' page, this will show an empty menu, since no level 3 pages are currently active.
        """
        with self.assertNumQueries(1):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 3 5 "all_descendants" %}',
                '<ul></ul>', {
                    'user': self.anon,
                    'fiber_page': self.home
                })

    def test_show_menu_main_3_5_all_descendants_on_disclaimer(self):
        """
        When visiting the 'disclaimer' page, this will show an empty menu, since no level 3 pages are currently active.
        """
        with self.assertNumQueries(1):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 3 5 "all_descendants" %}',
                '<ul></ul>', {
                    'user': self.anon,
                    'fiber_page': self.disclaimer
                })


class TestShowSitemap(BaseTestShowMenu):
    menu_1_2_all = '''
    <ul>
        <li class="about">
            <a href="/about/">about</a>
            <ul>
                <li class="mission first"><a href="/about/mission/">mission</a></li>
                <li class="people last"><a href="/about/people/">people</a></li>
            </ul>
        </li>
        <li class="news"><a href="/news/">news</a></li>
        <li class="products">
            <a href="/products/">products</a>
            <ul>
                <li class="product-a first"><a href="/products/product-a/">product a</a></li>
                <li class="product-b"><a href="/products/product-b/">product b</a></li>
            </ul>
        </li>
        <li class="contact last">
            <a href="/contact/">contact</a>
            <ul>
                <li class="newsletter first"><a href="/contact/newsletter/">newsletter</a></li>
                <li class="directions last"><a href="/contact/directions/">directions</a></li>
            </ul>
        </li>
    </ul>
    <ul>
        <li class="disclaimer first"><a href="/disclaimer/">disclaimer</a></li>
        <li class="privacy last"><a href="/privacy/">privacy</a></li>
    </ul>'''

    def test_show_menu_main_1_2_al_general_1_2_all_on_home(self):
        """
        On 'home' page show all pages, with all 2nd level pages expanded
        """
        with self.assertNumQueries(4):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 1 2 "all" %}{% show_menu "general" 1 2 "all" %}',
                self.menu_1_2_all, {
                    'user': self.anon,
                    'fiber_page': self.home
                })

    def test_show_menu_main_1_2_al_general_1_2_all_on_disclaimer(self):
        """
        On 'disclaimer' page show all pages, with all 2nd level pages expanded
        """
        with self.assertNumQueries(4):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 1 2 "all" %}{% show_menu "general" 1 2 "all" %}',
                self.menu_1_2_all, {
                    'user': self.anon,
                    'fiber_page': self.disclaimer
                })

    def test_show_menu_main_1_2_al_general_1_2_all_on_non_fiber_page(self):
        """
        On non-fiber page show all pages, with all 2nd level pages expanded
        """
        with self.assertNumQueries(4):
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 1 2 "all" %}{% show_menu "general" 1 2 "all" %}',
                self.menu_1_2_all, {
                    'user': self.anon
                })


class TestEdgeCases(TestCase):
    def test_show_non_existing_menu(self):
        """Rendering a non-existing menu raises a specific Page.DoesNotExist exception"""
        with self.assertRaises(Page.DoesNotExist) as cm:
            Template('{% load fiber_tags %}{% show_menu "missing" 1 999 %}').render(Context())
        self.assertEqual(str(cm.exception), "Menu does not exist.\nNo top-level page found with the title 'missing'.")


class TestStaffMenu(BaseTestShowMenu):
    def setUp(self):
        super().setUp()
        self.staff = User.objects.create_user('staff', 'staff@example.com', password='staff')
        self.staff.is_staff = True
        self.staff.save()

    def test_show_staff_menu(self):
        """Render a menu for a staff user"""

        with self.assertNumQueries(2):
            change_page = 'fiber_admin:fiber_page_change'
            self.assertRendered(
                '{% load fiber_tags %}{% show_menu "main" 1 1 "all" %}',
                '''
                <ul data-fiber-data='{ "type": "page", "add_url": "%(add_url)s", "parent_id": %(menu_pk)s }'>
                    <li class="home first df-non-public">
                        <a href="/" data-fiber-data='{ "can_edit": true, "type": "page", "id": %(home_pk)s, "parent_id": %(menu_pk)s, "url": "%(edit_url_home)s", "add_url": "%(add_url)s" }'>home</a>
                    </li>
                    <li class="about">
                        <a href="/about/" data-fiber-data='{ "can_edit": true, "type": "page", "id": %(about_pk)s, "parent_id": %(menu_pk)s, "url": "%(edit_url_about)s", "add_url": "%(add_url)s" }'>about</a>
                    </li>
                    <li class="news">
                        <a href="/news/" data-fiber-data='{ "can_edit": true, "type": "page", "id": %(news_pk)s, "parent_id": %(menu_pk)s, "url": "%(edit_url_news)s", "add_url": "%(add_url)s" }'>news</a>
                    </li>
                    <li class="products">
                        <a href="/products/" data-fiber-data='{ "can_edit": true, "type": "page", "id": %(products_pk)s, "parent_id": %(menu_pk)s, "url": "%(edit_url_products)s", "add_url": "%(add_url)s" }'>products</a>
                    </li>
                    <li class="contact last">
                        <a href="/contact/" data-fiber-data='{ "can_edit": true, "type": "page", "id": %(contact_pk)s, "parent_id": %(menu_pk)s, "url": "%(edit_url_contact)s", "add_url": "%(add_url)s" }'>contact</a>
                    </li>
                </ul>''' % {
                    'menu_pk': self.main.pk,
                    'add_url': reverse('fiber_admin:fiber_page_add'),
                    'home_pk': self.home.pk,
                    'edit_url_home': reverse(change_page, args=[self.home.pk]),
                    'about_pk': self.about.pk,
                    'edit_url_about': reverse(change_page, args=[self.about.pk]),
                    'news_pk': self.news.pk,
                    'edit_url_news': reverse(change_page, args=[self.news.pk]),
                    'products_pk': self.products.pk,
                    'edit_url_products': reverse(change_page, args=[self.products.pk]),
                    'contact_pk': self.contact.pk,
                    'edit_url_contact': reverse(change_page, args=[self.contact.pk])
                }, {
                    'user': self.staff,
                    'fiber_page': self.home
                })

    def test_render_empty_menu_1_1_for_staff(self):
        """
        When a staff member visits a page with an empty menu (created from level 1) allow adding pages to that menu.
        """
        menu = Page.objects.create(title='empty')
        self.assertRendered(
            '{% load fiber_tags %}{% show_menu "empty" 1 1 %}',
            '''
            <ul data-fiber-data='{ "type": "page", "add_url": "%(add_url)s", "parent_id": %(menu_pk)s }'></ul>
            ''' % {
                'menu_pk': menu.pk,
                'add_url': reverse('fiber_admin:fiber_page_add')
            }, {
                'user': self.staff,
                'fiber_page': self.home
            })

    def test_render_empty_menu_3_5_for_staff(self):
        """
        When a staff member visits a page with an empty menu (not created from level 1) don't allow adding pages!
        """
        self.assertRendered(
            '{% load fiber_tags %}{% show_menu "main" 3 5 %}',
            '''
            <ul></ul>
            ''', {
                'user': self.staff,
                'fiber_page': self.home
            })
