import re
import random

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.template import loader, RequestContext
from django.utils.encoding import smart_unicode
from django.utils import simplejson

from utils.import_util import import_element

from app_settings import EXCLUDE_URLS, EDITOR
from models import Page, ContentItem
from views import page


class PageFallbackMiddleware(object):

    def process_response(self, request, response):
        if response.status_code != 404:
            return response # No need to check for a page for non-404 responses.
        try:
            return page(request, request.path_info)
        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except Http404:
            return response
        except:
            if settings.DEBUG:
                raise
            return response


class AdminPageMiddleware(object):
    body_re = re.compile(
        r"<head>(?P<IN_HEAD>.*)</head>(?P<AFTER_HEAD>.*)<body(?P<IN_BODY_TAG>.*?)>(?P<BODY_CONTENTS>.*)</body>",
        re.DOTALL,
    )

    def __init__(self):
        self.editor_settings = self.get_editor_settings()

    def process_response(self, request, response):
        if self.set_login_session(request, response):
            request.session['show_fiber_admin'] = True
            url_without_fiber = request.path.replace('@fiber', '')
            querystring_without_fiber = ''
            if request.META['QUERY_STRING']:
                querystring_without_fiber = request.META['QUERY_STRING'].replace('@fiber', '')
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
                            'menus': Page.tree.root_nodes(),
                            'content_groups': ContentItem.objects.get_content_groups(),
                            'logout_url': self.get_logout_url(request),
                        })

                        # Inject admin html in body.
                        response.content = self.body_re.sub(
                            r"<head>\g<IN_HEAD></head>\g<AFTER_HEAD><body\g<IN_BODY_TAG>>%s\g<BODY_CONTENTS></body>" % ('<div id="wpr-body">',),
                            smart_unicode(response.content)
                        ).replace('</body>', '</div>' + t.render(c) + '</body>')

                        fiber_data['frontend'] = True
                        if 'fiber_page' in c:
                            fiber_data['page_id'] = c['fiber_page'].id

                # Inject header html in head.
                # Add fiber-data attribute to body tag.
                response.content = self.body_re.sub(
                    r"<head>\g<IN_HEAD>%s</head>\g<AFTER_HEAD><body data-fiber-data='%s'\g<IN_BODY_TAG>>\g<BODY_CONTENTS></body>" % (
                        self.get_header_html(request),
                        simplejson.dumps(fiber_data),
                    ),
                    smart_unicode(response.content)
                )

        return response

    def set_login_session(self, request, response):
        """
        Only set the fiber show_login session when the request
        - has @fiber behind its request-url
        """
        if response['Content-Type'].split(';')[0] not in ('text/html', 'application/xhtml+xml'):
            return False
        if not (request.path.endswith('@fiber') or (request.META['QUERY_STRING'] and request.META['QUERY_STRING'].endswith('@fiber'))):
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
        - has a response which is either 'text/html' or 'application/xhtml+xml'
        - is not an AJAX request
        - does not match EXCLUDE_URLS (empty by default)
        """
        if response.status_code != 200:
            return False
        if not hasattr(request, 'user'):
            return False
        if not request.user.is_staff:
            return False
        if response['Content-Type'].split(';')[0] not in ('text/html', 'application/xhtml+xml'):
            return False
        if request.is_ajax():
            return False
        if EXCLUDE_URLS:
            for exclude_url in EXCLUDE_URLS:
                if re.search(exclude_url, request.path.lstrip('/')):
                    return False
        return True

    def is_django_admin(self, request):
        return re.search(r'^%s' % (reverse('admin:index').lstrip('/')), request.path.lstrip('/'))

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
            return '%s?next=%s?%s' % (reverse('admin:logout'), request.path, request.META['QUERY_STRING'])
        else:
            return '%s?next=%s' % (reverse('admin:logout'), request.path)

    def get_editor_settings(self):
        return import_element(EDITOR)


class ObfuscateEmailAddressMiddleware(object):

    def process_response(self, request, response):
        # http://www.lampdocs.com/blog/2008/10/regular-expression-to-extract-all-e-mail-addresses-from-a-file-with-php/
        email_pattern = re.compile(r'(mailto:)?[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.(([0-9]{1,3})|([a-zA-Z]{2,3})|(aero|coop|info|museum|name))')
        if response['Content-Type'].split(';')[0] in ('text/html', 'application/xhtml+xml'):
            response.content = email_pattern.sub(self.encode_string_repl, response.content)
        return response

    def encode_string_repl(self, email_pattern_match):
        encoded_char_list = []
        for char in email_pattern_match.group(0):
            encoded_char_list.append(random.choice(['&#%d;' % ord(char), '&#x%x;' % ord(char)]))

        return ''.join(encoded_char_list)
