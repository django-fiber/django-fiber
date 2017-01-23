import random
import re
import json

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import loader, RequestContext
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.six.moves.urllib_parse import unquote

from fiber.app_settings import LOGIN_STRING, EXCLUDE_URLS, EDITOR, PERMISSION_CLASS
from fiber.models import ContentItem, Page
from fiber.utils.import_util import import_element, load_class


perms = load_class(PERMISSION_CLASS)


def is_html(response):
    """
    Returns True if the response is either `text/html` or `application/xhtml+xml`
    """
    content_type = response.get('Content-Type', None)
    return bool(content_type and content_type.split(';')[0] in ('text/html', 'application/xhtml+xml'))


class AdminPageMiddleware(object):
    LOGIN_SESSION_KEY = 'show_fiber_login'
    body_re = re.compile(
        r'<head>(?P<HEAD>.*)</head>(?P<AFTER_HEAD>.*)<body(?P<BODY_ATTRS>.*?)>(?P<BODY>.*)</body>',
        re.DOTALL)

    def __init__(self):
        self.editor_settings = import_element(EDITOR)

    def process_response(self, request, response):
        # only process non-streaming html and xhtml responses
        if is_html(response) and hasattr(response, 'content'):
            if self.should_setup_login_session(request):
                return self.setup_login_session(request)
            if self.show_login(request) or self.show_admin(request, response):
                return self.modify_response(request, response)
        return response

    def should_setup_login_session(self, request):
        """
        Only set self.LOGIN_SESSION_KEY in the session when the request
        - has LOGIN_STRING (defaults to @fiber) behind its request-url
        """
        qs = unquote(request.META.get('QUERY_STRING', ''))
        return request.path_info.endswith(LOGIN_STRING) or qs.endswith(LOGIN_STRING)

    def setup_login_session(self, request):
        """
        Add self.LOGIN_SESSION_KEY to the session and redirect to the the requested path without LOGIN_STRING
        """
        request.session[self.LOGIN_SESSION_KEY] = True
        url = request.path_info.replace(LOGIN_STRING, '')
        qs = unquote(request.META.get('QUERY_STRING', ''))
        if qs:
            qs = '?%s' % qs.replace(LOGIN_STRING, '').rstrip('&')
        return HttpResponseRedirect(''.join([url, qs]))

    def show_login(self, request):
        """
        Only show the Fiber login interface when the request
        - is NOT performed by an admin user
        - has session key self.LOGIN_SESSION_KEY = True
        """
        return not request.user.is_staff and request.session.get(self.LOGIN_SESSION_KEY)

    def show_admin(self, request, response):
        """
        Only show the Fiber admin interface when the request
        - is not an AJAX request
        - has a response status code of 200
        - is performed by an admin user
        - has a user with sufficient permissions based on the Permission Class
        - does not match EXCLUDE_URLS (empty by default)
        """
        if request.is_ajax() or response.status_code != 200:
            return False
        if request.user.is_staff and perms.is_fiber_editor(request.user):
            if EXCLUDE_URLS:
                url = request.path_info.lstrip('/')
                for exclude_url in EXCLUDE_URLS:
                    if re.search(exclude_url, url):
                        return False
            return True
        return False

    def modify_response(self, request, response):
        """
        Modify the response to include Fiber assets and data.
        """
        fiber_data = {}
        replacement = r'<head>\g<HEAD>%(header_html)s</head>\g<AFTER_HEAD><body data-fiber-data="%(fiber_data)s"\g<BODY_ATTRS>>\g<BODY></body>'
        content = force_text(response.content)
        if self.show_login(request):
            # Only show the login window once
            request.session[self.LOGIN_SESSION_KEY] = False
            fiber_data['show_login'] = True
        elif self.show_admin(request, response):
            if self.is_django_admin(request):
                fiber_data['backend'] = True
            else:
                fiber_data['frontend'] = True
                page = Page.objects.get_by_url(request.path_info)
                if page:
                    fiber_data['page_id'] = page.pk

                # Inject admin html in body, wrap the original body content in a div.
                replacement = r'<head>\g<HEAD>%(header_html)s</head>\g<AFTER_HEAD><body data-fiber-data="%(fiber_data)s"\g<BODY_ATTRS>><div id="wpr-body">\g<BODY></body>'
                content = content.replace('</body>', '</div>%s</body>' % self.get_body_html(request))

        # Inject header html in head.
        # Add fiber-data attribute to body tag.
        replacement = replacement % {
            'header_html': self.get_header_html(request),
            'fiber_data': escape(json.dumps(fiber_data, sort_keys=True))
        }
        response.content = self.body_re.sub(replacement, content)
        return response

    def is_django_admin(self, request):
        return request.path_info.startswith(reverse('admin:index'))

    def get_header_html(self, request):
        context = {
            'editor_template_js': self.editor_settings.get('template_js'),
            'editor_template_css': self.editor_settings.get('template_css'),
            'BACKEND_BASE_URL': reverse('admin:index'),
            'FIBER_LOGIN_URL': reverse('fiber_login'),
        }
        return loader.render_to_string('fiber/header.html', context, request=request)

    def get_body_html(self, request):
        context = {
            'logout_url': self.get_logout_url(request)
        }
        return loader.render_to_string('fiber/admin.html', context, request=request)

    def get_logout_url(self, request):
        if request.META['QUERY_STRING']:
            return '%s?next=%s?%s' % (reverse('admin:logout'), request.path_info, request.META['QUERY_STRING'])
        else:
            return '%s?next=%s' % (reverse('admin:logout'), request.path_info)

class ObfuscateEmailAddressMiddleware(object):
    """
    Replaces plain email addresses with escaped addresses in (non streaming) HTML responses
    """
    def process_response(self, request, response):
        if is_html(response) and hasattr(response, 'content'):  # Do not obfuscate non-html and streaming responses.
            # http://www.lampdocs.com/blog/2008/10/regular-expression-to-extract-all-e-mail-addresses-from-a-file-with-php/
            email_pattern = re.compile(r'(mailto:)?[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*(\+[_a-zA-Z0-9-]+)?@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.(([0-9]{1,3})|([a-zA-Z]{2,3})|(aero|coop|info|museum|name))')
            response.content = email_pattern.sub(self.encode_email, force_text(response.content))
        return response

    def encode_email(self, matches):
        encoded_char_list = []
        for char in matches.group(0):
            encoded_char_list.append(random.choice(['&#%d;' % ord(char), '&#x%x;' % ord(char)]))
        return ''.join(encoded_char_list)
