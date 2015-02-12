import random
import re
import json
from urllib import unquote

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import loader, RequestContext
from django.utils.encoding import smart_unicode

from .app_settings import LOGIN_STRING, EXCLUDE_URLS, EDITOR
from .models import ContentItem, Page
from .utils.import_util import import_element, load_class
from .app_settings import PERMISSION_CLASS


perms = load_class(PERMISSION_CLASS)


def is_html(response):
    """
    Returns True if the response is either `text/html` or `application/xhtml+xml`
    """
    content_type = response.get('Content-Type', None)
    return bool(content_type and content_type.split(';')[0] in ('text/html', 'application/xhtml+xml'))


class AdminPageMiddleware(object):
    body_re = re.compile(
        r"<head>(?P<IN_HEAD>.*)</head>(?P<AFTER_HEAD>.*)<body(?P<IN_BODY_TAG>.*?)>(?P<BODY_CONTENTS>.*)</body>",
        re.DOTALL,
    )

    def __init__(self):
        self.editor_settings = self.get_editor_settings()

    def process_response(self, request, response):
        # only process html and xhtml responses
        if not is_html(response):
            return response

        if self.set_login_session(request, response):
            request.session['show_fiber_admin'] = True
            url = request.path_info.replace(LOGIN_STRING, '')
            qs = unquote(request.META.get('QUERY_STRING', ''))
            if qs:
                qs = '?%s' % qs.replace(LOGIN_STRING, '').rstrip('&')
            return HttpResponseRedirect(''.join([url, qs]))
        else:
            fiber_data = {}

            is_login = self.show_login(request, response)
            if is_login or self.show_admin(request, response):
                if is_login:
                    # Only show the login window once
                    request.session['show_fiber_admin'] = False

                    fiber_data['show_login'] = True
                else:
                    if self.is_django_admin(request):
                        fiber_data['backend'] = True
                    else:
                        t = loader.get_template('fiber/admin.html')
                        c = RequestContext(request, {
                            'logout_url': self.get_logout_url(request),
                            'pages_json': json.dumps(
                                Page.objects.create_jqtree_data(request.user)
                            ),
                            'content_items_json': json.dumps(
                                ContentItem.objects.get_content_groups(request.user)
                            )
                        })

                        # Inject admin html in body.
                        response.content = self.body_re.sub(
                            r"<head>\g<IN_HEAD></head>\g<AFTER_HEAD><body\g<IN_BODY_TAG>>%s\g<BODY_CONTENTS></body>" % ('<div id="wpr-body">',),
                            smart_unicode(response.content)
                        ).replace('</body>', '</div>' + t.render(c) + '</body>')

                        fiber_data['frontend'] = True
                        try:
                            fiber_data['page_id'] = Page.objects.get_by_url(request.path_info).pk
                        except AttributeError:
                            pass

                # Inject header html in head.
                # Add fiber-data attribute to body tag.
                response.content = self.body_re.sub(
                    r"<head>\g<IN_HEAD>%s</head>\g<AFTER_HEAD><body data-fiber-data='%s'\g<IN_BODY_TAG>>\g<BODY_CONTENTS></body>" % (
                        self.get_header_html(request),
                        json.dumps(fiber_data),
                    ),
                    smart_unicode(response.content)
                )

        return response

    def set_login_session(self, request, response):
        """
        Only set the fiber show_login session when the request
        - has LOGIN_STRING (defaults to @fiber) behind its request-url
        """
        qs = unquote(request.META.get('QUERY_STRING', ''))
        return is_html(response) and (request.path_info.endswith(LOGIN_STRING) or qs.endswith(LOGIN_STRING))

    def show_login(self, request, response):
        """
        Only show the Fiber login interface when the request
        - has a response which is either 'text/html' or 'application/xhtml+xml'
        - is NOT performed by an admin user
        - has session key show_fiber_admin = True
        """
        if is_html(response):
            return not request.user.is_staff and request.session.get('show_fiber_admin')
        return False

    def show_admin(self, request, response):
        """
        Only show the Fiber admin interface when the request
        - has a response which is either 'text/html' or 'application/xhtml+xml'
        - is not an AJAX request
        - has a response status code of 200
        - is performed by an admin user
        - has a user with sufficient permissions based on the Permission Class
        - does not match EXCLUDE_URLS (empty by default)
        """
        if request.is_ajax() or not is_html(response) or response.status_code != 200:
            return False
        if request.user.is_staff and perms.is_fiber_editor(request.user):
            if EXCLUDE_URLS:
                url = request.path_info.lstrip('/')
                for exclude_url in EXCLUDE_URLS:
                    if re.search(exclude_url, url):
                        return False
            return True
        return False

    def is_django_admin(self, request):
        return request.path_info.startswith(reverse('admin:index'))

    def get_header_html(self, request):
        t = loader.get_template('fiber/header.html')
        c = RequestContext(
            request,
            {
                'editor_template_js': self.editor_settings.get('template_js'),
                'editor_template_css': self.editor_settings.get('template_css'),
                'BACKEND_BASE_URL': reverse('admin:index'),
                'FIBER_LOGIN_URL': reverse('fiber_login'),
            },
        )
        return t.render(c)

    def get_logout_url(self, request):
        if request.META['QUERY_STRING']:
            return '%s?next=%s?%s' % (reverse('admin:logout'), request.path_info, request.META['QUERY_STRING'])
        else:
            return '%s?next=%s' % (reverse('admin:logout'), request.path_info)

    def get_editor_settings(self):
        return import_element(EDITOR)


class ObfuscateEmailAddressMiddleware(object):
    """
    Replaces plain email addresses with escaped addresses in (non streaming) HTML responses
    """
    def process_response(self, request, response):
        if is_html(response) and hasattr(response, 'content'):  # Do not obfuscate non-html and streaming responses.
            # http://www.lampdocs.com/blog/2008/10/regular-expression-to-extract-all-e-mail-addresses-from-a-file-with-php/
            email_pattern = re.compile(r'(mailto:)?[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*(\+[_a-zA-Z0-9-]+)?@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.(([0-9]{1,3})|([a-zA-Z]{2,3})|(aero|coop|info|museum|name))')
            response.content = email_pattern.sub(self.encode_email, response.content)
        return response

    def encode_email(self, matches):
        encoded_char_list = []
        for char in matches.group(0):
            encoded_char_list.append(random.choice(['&#%d;' % ord(char), '&#x%x;' % ord(char)]))
        return ''.join(encoded_char_list)
