import random
import re
import json

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import loader, RequestContext
from django.utils.encoding import smart_unicode

from .app_settings import LOGIN_STRING, EXCLUDE_URLS, EDITOR
from .models import ContentItem, Page
from .utils.import_util import import_element
from .utils.class_loader import load_class
from .app_settings import PERMISSION_CLASS


def is_non_html(response):
    """
    Returns True if the response has no Content-type set or is not `text/html`
    or not `application/xhtml+xml`.
    """

    content_type = response.get('Content-Type', None)
    if content_type is None or content_type.split(';')[0] not in ('text/html', 'application/xhtml+xml'):
        return True


class AdminPageMiddleware(object):
    body_re = re.compile(
        r"<head>(?P<IN_HEAD>.*)</head>(?P<AFTER_HEAD>.*)<body(?P<IN_BODY_TAG>.*?)>(?P<BODY_CONTENTS>.*)</body>",
        re.DOTALL,
    )

    def __init__(self):
        self.editor_settings = self.get_editor_settings()

    def process_response(self, request, response):
        # only process html and xhtml responses
        if is_non_html(response):
            return response

        if self.set_login_session(request, response):
            request.session['show_fiber_admin'] = True
            url_without_fiber = request.path_info.replace(LOGIN_STRING, '')
            querystring_without_fiber = ''
            if request.META['QUERY_STRING']:
                querystring_without_fiber = request.META['QUERY_STRING'].replace(LOGIN_STRING, '')
            if (querystring_without_fiber != ''):
                querystring = '?%s' % querystring_without_fiber
            else:
                querystring = ''

            return HttpResponseRedirect('%s%s' % (url_without_fiber, querystring))
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
        if response['Content-Type'].split(';')[0] not in ('text/html', 'application/xhtml+xml'):
            return False
        if not (request.path_info.endswith(LOGIN_STRING) or (request.META['QUERY_STRING'] and request.META['QUERY_STRING'].endswith(LOGIN_STRING))):
            return False
        else:
            return True

    def show_login(self, request, response):
        """
        Only show the Fiber login interface when the request
        - is not performed by an admin user
        - has session key show_fiber_admin = True
        - has a response which is either 'text/html' or 'application/xhtml+xml'
        """
        if response['Content-Type'].split(';')[0] not in ('text/html', 'application/xhtml+xml'):
            return False
        try:
            if request.user.is_staff:
                return False
        except AttributeError:
            pass
        try:
            if not request.session['show_fiber_admin'] == True:
                return False
        except AttributeError:
            return False
        except KeyError:
            return False
        else:
            return True

    def show_admin(self, request, response):
        """
        Only show the Fiber admin interface when the request
        - has a response status code of 200
        - is performed by an admin user
        - has a user with sufficient permissions based on the Permission Class
        - has a response which is either 'text/html' or 'application/xhtml+xml'
        - is not an AJAX request
        - does not match EXCLUDE_URLS (empty by default)
        """
        if response.status_code != 200:
            return False
        if not hasattr(request, 'user'):
            return False
        if not load_class(PERMISSION_CLASS).is_fiber_editor(request.user):
            return False
        if not request.user.is_staff:
            return False
        if response['Content-Type'].split(';')[0] not in ('text/html', 'application/xhtml+xml'):
            return False
        if request.is_ajax():
            return False
        if EXCLUDE_URLS:
            for exclude_url in EXCLUDE_URLS:
                if re.search(exclude_url, request.path_info.lstrip('/')):
                    return False
        return True

    def is_django_admin(self, request):
        return re.search(r'^%s' % (reverse('admin:index').lstrip('/')), request.path_info.lstrip('/'))

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

    def process_response(self, request, response):
        # http://www.lampdocs.com/blog/2008/10/regular-expression-to-extract-all-e-mail-addresses-from-a-file-with-php/
        email_pattern = re.compile(r'(mailto:)?[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.(([0-9]{1,3})|([a-zA-Z]{2,3})|(aero|coop|info|museum|name))')
        if is_non_html(response):
            return response
        response.content = email_pattern.sub(self.encode_string_repl, response.content)
        return response

    def encode_string_repl(self, email_pattern_match):
        encoded_char_list = []
        for char in email_pattern_match.group(0):
            encoded_char_list.append(random.choice(['&#%d;' % ord(char), '&#x%x;' % ord(char)]))

        return ''.join(encoded_char_list)
