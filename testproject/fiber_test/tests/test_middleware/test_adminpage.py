import re
from unittest import skipUnless

from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpResponse, StreamingHttpResponse
from django.test import RequestFactory, TestCase, SimpleTestCase
from django.utils.encoding import force_str

import fiber.middleware

from fiber.middleware import AdminPageMiddleware
from fiber.models import ContentItem, Page, PageContentItem

middleware = AdminPageMiddleware(lambda: None)


class TestAtFiberLoginRedirect(TestCase):
    """Test the actual @fiber login logic"""

    def test_login_session_key_in_session(self):
        """Middleware sets LOGIN_SESSION_KEY session variable"""
        self.client.get('/empty/@fiber')
        self.assertIn(middleware.LOGIN_SESSION_KEY, self.client.session)
        self.assertTrue(self.client.session[middleware.LOGIN_SESSION_KEY])

    def test_response_redirect(self):
        """Middleware strips @fiber from path"""
        response = self.client.get('/empty/@fiber')
        self.assertRedirects(response, '/empty/')

    def test_response_redirect_querystring(self):
        """Middleware strips @fiber from path, querystring stays intact"""
        response = self.client.get('/empty/@fiber?foo=bar&baz=qux')
        self.assertRedirects(response, '/empty/?foo=bar&baz=qux')

    def test_response_redirect_querystring_with_fiber(self):
        """Middleware strips @fiber from querystring"""
        response = self.client.get('/empty/?%40fiber')
        self.assertRedirects(response, '/empty/?')

    def test_response_redirect_querystring_and_at_fiber(self):
        """Middleware strips @fiber from querystring, rest of qs stays intact"""
        response = self.client.get('/empty/?foo=bar&baz=qux&%40fiber')
        self.assertRedirects(response, '/empty/?foo=bar&baz=qux')

    def test_follow_redirect_sets_login_session_key_to_false(self):
        """Following the redirect sets LOGIN_SESSION_KEY to False"""
        self.client.get('/empty/@fiber', follow=True)
        self.assertFalse(self.client.session[middleware.LOGIN_SESSION_KEY])

    def test_follow_redirect_shows_login_in_body(self):
        """Following the redirect adds fiber-data to body"""
        response = self.client.get('/empty/@fiber', follow=True)
        self.assertRegex(force_str(response.content), '<body data-fiber-data="{&quot;show_login&quot;: true}"></body>')

    def test_does_nothing_for_non_html_response(self):
        """Middleware skips non-html responses"""
        request = self.client.get('/@fiber')
        request.session = {}
        response = HttpResponse('', content_type='application/json')
        middleware.process_response(request, response)
        self.assertNotIn(middleware.LOGIN_SESSION_KEY, request.session)

    @skipUnless(StreamingHttpResponse, 'StreamingHttpResponse is not available')
    def test_skips_streaming(self):
        """Streaming responses don't get touched"""
        request = self.client.get('/@fiber')
        request.session = {}
        response = StreamingHttpResponse('')
        middleware.process_response(request, response)
        self.assertNotIn(middleware.LOGIN_SESSION_KEY, request.session)


class TestModifiedResponse(TestCase):
    def setUp(self):
        # Setup u a session with a logged in user
        self.staff = User.objects.create_user('staff', 'staff@example.com', password='staff')
        self.staff.is_staff = True
        self.staff.save()
        self.client.login(username='staff', password='staff')
        # Create a test fiber page
        page = Page.objects.create(title='home', url='/')
        lipsum = ContentItem.objects.create(content_html='lorem ipsum')
        PageContentItem.objects.create(page=page, content_item=lipsum, block_name='main')
        self.page = page

    def test_get_admin_url(self):
        response = self.client.get('/admin/')
        self.assertRegex(force_str(response.content), '<body data-fiber-data="{&quot;backend&quot;: true}"')

    def test_get_frontend_url(self):
        response = self.client.get('/empty/')
        self.assertRegex(force_str(response.content), '<body data-fiber-data="{&quot;frontend&quot;: true}"')

    def test_wraps_body(self):
        response = self.client.get(self.page.get_absolute_url())
        self.assertRegex(force_str(response.content),
                         re.compile('<div id="wpr-body">.*lorem ipsum.*</div>', re.DOTALL))

    def test_set_page_id(self):
        response = self.client.get(self.page.get_absolute_url())
        expected = '<body data-fiber-data="{&quot;frontend&quot;: true, &quot;page_id&quot;: %s}"' % self.page.pk
        self.assertRegex(force_str(response.content), expected)

    def test_adds_sidebar(self):
        response = self.client.get('/empty/')
        self.assertIn('<div id="df-sidebar">', force_str(response.content))

    @skipUnless(StreamingHttpResponse, 'StreamingHttpResponse is not available')
    def test_skips_streaming(self):
        """
        Streaming responses don't get touched
        """
        request = RequestFactory().get('/')
        content = ''
        response = StreamingHttpResponse(content)
        self.assertEqual(''.join(middleware.process_response(request, response)), content)


class TestResponseNotModified(TestCase):
    def test_get_frontend_url(self):
        """
        A normal request has no trace of fiber
        """
        response = self.client.get('/empty/')
        self.assertNotIn('data-fiber-data', force_str(response.content))
        self.assertNotIn('<div id="df-sidebar">', force_str(response.content))


class TestSetLoginSessionMethod(TestCase):
    """Test middleware.set_login_session"""
    client_class = RequestFactory

    def test_at_fiber_in_path(self):
        """@fiber is at the end"""
        request = self.client.get('/@fiber')
        self.assertTrue(middleware.should_setup_login_session(request))

    def test_at_fiber_in_path_with_qs(self):
        """@fiber is at the end, there's also a query string"""
        request = self.client.get('/@fiber', {'foo': 'bar'})
        self.assertTrue(middleware.should_setup_login_session(request))

    def test_at_fiber_in_qs_value(self):
        """@fiber is at the end, as a query value"""
        request = self.client.get('/?login=%40fiber')
        self.assertTrue(middleware.should_setup_login_session(request))

    def test_at_fiber_in_qs_key(self):
        """@fiber is at the end, as a query param"""
        request = self.client.get('/?%40fiber')
        self.assertTrue(middleware.should_setup_login_session(request))

    def test_qs_value_ends_with_at_fiber(self):
        """@fiber is at the end of some other value"""
        request = self.client.get('/?foo=bar%40fiber')
        self.assertTrue(middleware.should_setup_login_session(request))

    def test_at_fiber_in_qs_middle(self):
        """@fiber is NOT at the end"""
        request = self.client.get('/?%40fiber&foo=bar')
        self.assertFalse(middleware.should_setup_login_session(request))


class TestShowLoginMethod(TestCase):
    """Test middleware.show_login"""
    client_class = RequestFactory

    def setUp(self):
        self.user = User.objects.create_user('user', 'user@example.com', password='user')
        self.staff = User.objects.create_user('staff', 'staff@example.com', password='staff')
        self.staff.is_staff = True
        self.staff.save()

    def prepare_request(self, user, login_session_key=True):
        """Helper method to create requests"""
        request = self.client.get('/')
        request.user = user
        request.session = {middleware.LOGIN_SESSION_KEY: login_session_key}
        return request

    def test_anonymous(self):
        """Show login for anonymous (not logged in) user"""
        request = self.prepare_request(AnonymousUser())
        self.assertTrue(middleware.show_login(request))

    def test_non_staff(self):
        """Show login for non-staff in user"""
        request = self.prepare_request(self.user)
        self.assertTrue(middleware.show_login(request))

    def test_login_session_key_false(self):
        """Don't show login if LOGIN_SESSION_KEY is False"""
        request = self.prepare_request(self.staff, False)
        self.assertFalse(middleware.show_login(request))

    def test_empty_session(self):
        """Don't show login if LOGIN_SESSION_KEY is not in session"""
        request = self.prepare_request(self.staff)
        request.session = {}
        self.assertFalse(middleware.show_login(request))


class TestShowAdminMethod(TestCase):
    """Test middleware.show_admin"""
    client_class = RequestFactory

    def setUp(self):
        self.user = User.objects.create_user('user', 'user@example.com', password='user')
        self.staff = User.objects.create_user('staff', 'staff@example.com', password='staff')
        self.staff.is_staff = True
        self.staff.save()
        self._exclude_urls = fiber.middleware.EXCLUDE_URLS
        fiber.middleware.EXCLUDE_URLS = [
            '^exclude/'
        ]

    def tearDown(self):
        fiber.middleware.EXCLUDE_URLS = self._exclude_urls

    def test_staff(self):
        """Show admin for staff users"""
        request = self.client.get('/')
        request.user = self.staff
        response = HttpResponse('')
        self.assertTrue(middleware.show_admin(request, response))

    def test_anonymous(self):
        """Don't show admin for anonymous (not logged in) user"""
        request = self.client.get('/')
        request.user = AnonymousUser()
        response = HttpResponse('')
        self.assertFalse(middleware.show_admin(request, response))

    def test_non_staff(self):
        """Don't show admin for non-staff in user"""
        request = self.client.get('/')
        request.user = self.user
        response = HttpResponse('')
        self.assertFalse(middleware.show_admin(request, response))

    def test_404(self):
        """Don't show admin on error pages"""
        request = self.client.get('/')
        request.user = self.staff
        response = HttpResponse('', status=404)
        self.assertFalse(middleware.show_admin(request, response))

    def test_ajax(self):
        """Don't show admin on ajax requests"""
        request = self.client.get('/')
        request.user = self.staff
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        response = HttpResponse('')
        self.assertFalse(middleware.show_admin(request, response))

    def test_exclude_url(self):
        """Don't show admin on excluded urls"""
        request = self.client.get('/exclude/')
        request.user = self.staff
        response = HttpResponse('')
        self.assertFalse(middleware.show_admin(request, response))

    def test_exclude_url_2nd_level(self):
        """Don't show admin on excluded urls"""
        request = self.client.get('/exclude/sub/')
        request.user = self.staff
        response = HttpResponse('')
        self.assertFalse(middleware.show_admin(request, response))


class TestIsDjangoAdminMethod(TestCase):
    """Test middleware.is_django_admin"""
    client_class = RequestFactory

    def test_is_django_admin(self):
        request = self.client.get('/admin/')
        self.assertTrue(middleware.is_django_admin(request))

    def test_is_also_django_admin(self):
        request = self.client.get('/admin/fiber/')
        self.assertTrue(middleware.is_django_admin(request))

    def test_is_not_django_admin(self):
        request = self.client.get('/')
        self.assertFalse(middleware.is_django_admin(request))


class TestGetLogoutUrlMethod(TestCase):
    """Test middleware.get_logout_url"""
    client_class = RequestFactory

    def test_without_querystring(self):
        request = self.client.get('/')
        self.assertEqual('/admin/logout/?next=/', middleware.get_logout_url(request))

    def test_with_querystring(self):
        request = self.client.get('/', {'foo': 'bar'})
        self.assertEqual('/admin/logout/?next=/?foo=bar', middleware.get_logout_url(request))
