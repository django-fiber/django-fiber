import os

import html

from unittest import skipUnless

from django.http import HttpResponse, StreamingHttpResponse
from django.test import SimpleTestCase
from django.utils.encoding import force_str

from fiber.middleware import ObfuscateEmailAddressMiddleware


class TestEmailAddressObfuscation(SimpleTestCase):
    """Test the obfuscation method"""

    def setUp(self):
        self.middleware = ObfuscateEmailAddressMiddleware(lambda: None)

    def test_is_obfuscated(self):
        """Check if the given content is really not present in the response"""
        content = 'example@example.com'
        self.assertNotEqual(
            force_str(self.middleware.process_response(None, HttpResponse(content)).content),
            content)

    def test_is_html_escaped(self):
        """Unescape the escaped response to see if it's the original content"""
        content = 'example@example.com'
        self.assertEqual(html.unescape(
            force_str(self.middleware.process_response(None, HttpResponse(content)).content)),
            content)


class TestEmailAddressReplacement(SimpleTestCase):
    """Test if email addresses get detected, and replaced, correctly"""

    def setUp(self):
        """Mock the encoding method, so we can get predictable output"""
        self.middleware = ObfuscateEmailAddressMiddleware(lambda: None)
        self.middleware.encode_email = lambda email: '!!%s!!' % email

    def assertResponse(self, content, expected):
        """Little helper assertion to dry things up"""
        self.assertEqual(
            force_str(self.middleware.process_response(None, HttpResponse(content)).content),
            expected)

    def test_simple(self):
        email = 'niceandsimple@example.com'
        self.assertResponse(email, '!!%s!!' % email)

    def test_common(self):
        email = 'very.common@example.com'
        self.assertResponse(email, '!!%s!!' % email)

    def test_long(self):
        email = 'a.little.lengthy.but.fine@dept.example.com'
        self.assertResponse(email, '!!%s!!' % email)

    def test_with_plus_symbol(self):
        email = 'disposable.style.email.with+symbol@example.com'
        self.assertResponse(email, '!!%s!!' % email)

    def test_dashes(self):
        email = 'other.email-with-dash@example.com'
        self.assertResponse(email, '!!%s!!' % email)

    def test_replaces_single_email(self):
        self.assertResponse('Contact me at: spam@example.com', 'Contact me at: !!spam@example.com!!')

    def test_replaces_multiple_email_addresses(self):
        content = ('Contact me at: spam@example.com\n'
                   'my-friend@example.com is the email address of my friend\n'
                   'We share email@example.com for email')
        expected = ('Contact me at: !!spam@example.com!!\n'
                    '!!my-friend@example.com!! is the email address of my friend\n'
                    'We share !!email@example.com!! for email')
        self.assertResponse(content, expected)

    def test_replaces_single_email_in_anchor(self):
        content = 'Contact me at: <a href="mailto:spam@example.com">spam@example.com</a>'
        expected = 'Contact me at: <a href="!!mailto:spam@example.com!!">!!spam@example.com!!</a>'
        self.assertResponse(content, expected)

    def test_replaces_multiple_email_addresses_in_anchors(self):
        content = ('Contact me at: <a href="mailto:spam@example.com">spam@example.com</a>\n'
                   '<a href="mailto:my-friend@example.com">my-friend@example.com</a> is the email address of my friend\n'
                   'We share <a href="mailto:email@example.com">email@example.com</a> for email')
        expected = ('Contact me at: <a href="!!mailto:spam@example.com!!">!!spam@example.com!!</a>\n'
                    '<a href="!!mailto:my-friend@example.com!!">!!my-friend@example.com!!</a> is the email address of my friend\n'
                    'We share <a href="!!mailto:email@example.com!!">!!email@example.com!!</a> for email')
        self.assertResponse(content, expected)

    def test_replacement_in_brackets(self):
        content = 'Email Me <email@example.com>'
        expected = 'Email Me <!!email@example.com!!>'
        self.assertResponse(content, expected)

    def test_replacement_with_dot(self):
        content = 'Email Me email@example.com.'
        expected = 'Email Me !!email@example.com!!.'
        self.assertResponse(content, expected)

    def test_replacement_in_very_large_page(self):
        with open(os.path.join(os.path.dirname(__file__), 'very_large_page.html')) as f:
            content = f.read()
        output = force_str(self.middleware.process_response(None, HttpResponse(content)).content)
        self.assertIn('<a href="!!mailto:info@example.com!!">!!info@example.com!!</a>', output, msg='href not replaced')
        self.assertIn('<img alt="!!alt@example.com!!"', output, msg='alt not replaced')


class TestNonReplacement(SimpleTestCase):
    """Test that email addresses do not get replaced under certain circumstances"""

    def setUp(self):
        self.middleware = ObfuscateEmailAddressMiddleware(lambda: None)

    def test_skips_non_html(self):
        content = 'Contact me at: spam@example.com'
        response = HttpResponse(content, content_type='text/plain')
        self.assertEqual(
            force_str(self.middleware.process_response(None, response).content), content)

    @skipUnless(StreamingHttpResponse, 'StreamingHttpResponse is not available')
    def test_skips_streaming(self):
        content = 'Contact me at: spam@example.com'
        response = StreamingHttpResponse(content)
        self.assertEqual(''.join(force_str(s) for s in self.middleware.process_response(None, response)), content)

    def test_twitter_username(self):
        content = 'On twitter I am known as @example'
        response = HttpResponse(content)
        self.assertEqual(
            force_str(self.middleware.process_response(None, response).content), content)
