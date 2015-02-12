from django.contrib.auth.models import User, AnonymousUser
from django.http import HttpResponse
from django.test import TestCase, RequestFactory

import fiber.middleware
from fiber.middleware import AdminPageMiddleware


middleware = AdminPageMiddleware()


class TestSetLoginSessionMethod(TestCase):
    """Test middleware.set_login_session"""
    client_class = RequestFactory

    def test_at_fiber_in_path(self):
        """@fiber is at the end"""
        request = self.client.get('/@fiber')
        response = HttpResponse('')
        self.assertTrue(middleware.set_login_session(request, response))

    def test_at_fiber_in_path_with_qs(self):
        """@fiber is at the end, there's also a query string"""
        request = self.client.get('/@fiber', {'foo': 'bar'})
        response = HttpResponse('')
        self.assertTrue(middleware.set_login_session(request, response))

    def test_at_fiber_in_qs_value(self):
        """@fiber is at the end, as a query value"""
        request = self.client.get('/?login=%40fiber')
        response = HttpResponse('')
        self.assertTrue(middleware.set_login_session(request, response))

    def test_at_fiber_in_qs_key(self):
        """@fiber is at the end, as a query param"""
        request = self.client.get('/?%40fiber')
        response = HttpResponse('')
        self.assertTrue(middleware.set_login_session(request, response))

    def test_at_fiber_in_qs_middle(self):
        """@fiber is NOT at the end"""
        request = self.client.get('/?%40fiber&foo=bar')
        response = HttpResponse('')
        self.assertFalse(middleware.set_login_session(request, response))

    def test_at_fiber_in_path_non_html(self):
        """@fiber is at the end, NON html response"""
        request = self.client.get('/@fiber')
        response = HttpResponse('', content_type='application/json')
        self.assertFalse(middleware.set_login_session(request, response))


class TestAtFiberLoginRedirect(TestCase):
    """Test the actual @fiber login logic"""

    def test_show_fiber_admin_in_session(self):
        """Middleware sets show_fiber_admin session variable"""
        self.client.get('/empty/@fiber')
        self.assertIn('show_fiber_admin', self.client.session)
        self.assertTrue(self.client.session['show_fiber_admin'])

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
        self.assertRedirects(response, '/empty/')

    def test_response_redirect_querystring_and_at_fiber(self):
        """Middleware strips @fiber from querystring, rest of qs stays intact"""
        response = self.client.get('/empty/?foo=bar&baz=qux&%40fiber')
        self.assertRedirects(response, '/empty/?foo=bar&baz=qux')

    def test_follow_redirect_sets_show_fiber_admin_to_false(self):
        """Following the redirect sets session['show_fiber_admin'] to False"""
        self.client.get('/empty/@fiber', follow=True)
        self.assertFalse(self.client.session['show_fiber_admin'])

    def test_follow_redirect_shows_login_in_body(self):
        """Following the redirect adds fiber-data to body"""
        response = self.client.get('/empty/@fiber', follow=True)
        self.assertRegexpMatches(response.content, '<body data-fiber-data=\'{"show_login": true}\'></body>')

    def test_does_nothing_for_non_html_response(self):
        """Middleware skips non-html responses"""
        request = self.client.get('/@fiber')
        request.session = {}
        response = HttpResponse('', content_type='application/json')
        middleware.process_response(request, response)
        self.assertNotIn('show_fiber_admin', request.session)


class TestShowLoginMethod(TestCase):
    """Test middleware.show_login"""
    client_class = RequestFactory

    def setUp(self):
        self.user = User.objects.create_user('user', 'user@example.com', password='user')
        self.staff = User.objects.create_user('staff', 'staff@example.com', password='staff')
        self.staff.is_staff = True
        self.staff.save()

    def prepare_request(self, user, show_fiber_admin=True):
        """Helper method to create requests"""
        request = self.client.get('/')
        request.user = user
        request.session = {'show_fiber_admin': show_fiber_admin}
        return request

    def test_anonymous(self):
        """Show login for anonymous (not logged in) user"""
        request = self.prepare_request(AnonymousUser())
        response = HttpResponse('')
        self.assertTrue(middleware.show_login(request, response))

    def test_non_staff(self):
        """Show login for non-staff in user"""
        request = self.prepare_request(self.user)
        response = HttpResponse('')
        self.assertTrue(middleware.show_login(request, response))

    def test_show_fiber_admin_false(self):
        """Don't show login if show_fiber_admin is False"""
        request = self.prepare_request(self.staff, False)
        response = HttpResponse('')
        self.assertFalse(middleware.show_login(request, response))

    def test_empty_session(self):
        """Don't show login if show_fiber_admin is not in session"""
        request = self.prepare_request(self.staff)
        request.session = {}
        response = HttpResponse('')
        self.assertFalse(middleware.show_login(request, response))

    def test_non_html(self):
        """Don't show login on non-html responses"""
        request = self.prepare_request(self.staff)
        response = HttpResponse('', content_type='application/json')
        self.assertFalse(middleware.show_login(request, response))


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

    def test_non_html(self):
        """Don't show admin on non-html responses"""
        request = self.client.get('/')
        request.user = self.user
        response = HttpResponse('', content_type='application/json')
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


class TestModifiedResponse(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('staff', 'staff@example.com', password='staff')
        self.staff.is_staff = True
        self.staff.save()
        self.client.login(username='staff', password='staff')

    def test_get_admin_url(self):
        response = self.client.get('/admin/')
        self.assertRegexpMatches(response.content, '<body data-fiber-data=\'{"backend": true}\'')
