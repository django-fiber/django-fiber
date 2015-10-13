from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.test.utils import override_settings

from fiber.models import Page, ContentItem, PageContentItem
from fiber.views import FiberTemplateView


class TestFiberTemplateView(TestCase):
    def setUp(self):
        self.frontpage = Page.objects.create(title='frontpage', url='/')
        self.template_page = Page.objects.create(title='template page', url='/template-page/', template_name='template1.html')

    def test_get_fiber_page_url(self):
        """Returns request url"""
        view = FiberTemplateView()
        view.request = RequestFactory().get(self.frontpage.url)
        self.assertEqual(view.get_fiber_page_url(), self.frontpage.url)

    def test_get_fiber_page(self):
        """Returns requested page"""
        view = FiberTemplateView()
        view.request = RequestFactory().get(self.frontpage.url)
        self.assertEqual(view.get_fiber_page(), self.frontpage)

    def test_get_fiber_page_for_non_fiber_url(self):
        """Returns requested page"""
        view = FiberTemplateView()
        view.request = RequestFactory().get('/empty/')
        self.assertIsNone(view.get_fiber_page())

    def test_get_template_names_default(self):
        """Returns default template"""
        view = FiberTemplateView()
        view.request = RequestFactory().get(self.frontpage.url)
        self.assertEqual(view.get_template_names(), 'base.html')

    def test_get_template_names_from_page(self):
        """Returns custom template"""
        view = FiberTemplateView()
        view.request = RequestFactory().get(self.template_page.url)
        self.assertEqual(view.get_template_names(), 'template1.html')

    def test_renders_default_template(self):
        """Renders default template to response"""
        lipsum = ContentItem.objects.create(content_html='lorem ipsum')
        PageContentItem.objects.create(page=self.frontpage, content_item=lipsum, block_name='main')
        response = self.client.get(self.frontpage.url)
        self.assertContains(response, 'lorem ipsum')
        self.assertContains(response, '<title>frontpage</title>')

    def test_renders_custom_template(self):
        """Renders custom template to tesponse"""
        response = self.client.get(self.template_page.url)
        self.assertContains(response, 'This is template1.')

    def test_trailing_slash_redirect(self):
        """Handles APPEND_SLASH"""
        self.assertRedirects(self.client.get(self.template_page.url.rstrip('/')), self.template_page.url, 301)

    @override_settings(APPEND_SLASH=False)
    def test_no_trailing_slash_redirect(self):
        """Considers APPEND_SLASH config"""
        self.assertEqual(self.client.get(self.template_page.url.rstrip('/')).status_code, 404)

    def test_redirect_page(self):
        """Redirects to another page"""
        Page.objects.create(title='redirect', url='/redirect/', redirect_page=self.frontpage)
        self.assertRedirects(self.client.get('/redirect/'), self.frontpage.url, 301)

    def test_redirect_to_self(self):
        """Does not redirect to self"""
        page = Page.objects.create(title='redirect loop', url='/redirect-loop/')
        page.redirect_page = page
        page.save()
        self.assertEqual(self.client.get('/redirect-loop/').status_code, 200)

    def test_404_page(self):
        """Does not mask 404 pages"""
        self.assertEqual(self.client.get('/does-not-exists/').status_code, 404)

    def test_private_pages(self):
        """Hides private pages"""
        Page.objects.create(title='private', url='/private/', is_public=False)
        self.assertEqual(self.client.get('/private/').status_code, 404)

    def test_private_pages_for_staff(self):
        """Shows private pages"""
        staff = User.objects.create_user('staff', 'staff@example.com', password='staff')
        staff.is_staff = True
        staff.save()
        Page.objects.create(title='private', url='/private/', is_public=False)
        self.client.login(username='staff', password='staff')
        self.assertEqual(self.client.get('/private/').status_code, 200)
