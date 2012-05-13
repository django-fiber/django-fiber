import re

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponsePermanentRedirect, Http404
from django.views.generic.base import TemplateView

from app_settings import DEFAULT_TEMPLATE
from models import Page


class FiberPageMixin(object):
    fiber_page_url = None
    fiber_page = None
    fiber_current_pages = None

    def get_fiber_page_url(self):
        if self.fiber_page_url == None:
            raise ImproperlyConfigured(u"%(cls)s is missing a fiber_page_url. Define "
                u"%(cls)s.fiber_page_url, or override "
                u"%(cls)s.get_fiber_page_url()." % {
                'cls': self.__class__.__name__,
            })
        return self.fiber_page_url

    def get_fiber_page(self):
        if self.fiber_page == None:
            self.fiber_page = Page.objects.get_by_url(self.get_fiber_page_url())
        return self.fiber_page

    def get_fiber_current_pages(self):
        if self.fiber_current_pages == None:
            """
            start with an empty list
            """
            self.fiber_current_pages = []

            """
            Find pages that should be marked as current in menus.
            """
            if self.get_fiber_page() != None:
                """
                The current page should be marked as current, obviously,
                as well as all its ancestors.
                """

                self.fiber_current_pages.append(self.get_fiber_page())
                self.fiber_current_pages.extend(self.get_fiber_page().get_ancestors())

            """
            For all pages that are not already current_pages,
            check if one of the `mark_current_regexes` matches the requested URL.
            If so, add the page and all its ancestors to the current_pages list.
            """
            current_page_candidates = Page.objects.exclude(mark_current_regexes__exact='')
            url = self.get_fiber_page_url()

            for current_page_candidate in list(set(current_page_candidates) - set(self.fiber_current_pages)):
                for mark_current_regex in current_page_candidate.mark_current_regexes.strip().splitlines():
                    if re.match(mark_current_regex, url):
                        self.fiber_current_pages.append(current_page_candidate)
                        self.fiber_current_pages.extend(current_page_candidate.get_ancestors())
                        break

            """
            Order current_pages for use with tree_info template tag,
            and remove the root node in the process.
            """
            self.fiber_current_pages = sorted(self.fiber_current_pages, key=lambda fiber_current_page: fiber_current_page.lft)[1:]

        return self.fiber_current_pages


class FiberTemplateView(FiberPageMixin, TemplateView):

    def get_fiber_page_url(self):
        return self.request.path_info

    def get_context_data(self, **kwargs):
        context = super(FiberTemplateView, self).get_context_data(**kwargs)
        context['fiber_page'] = self.get_fiber_page()
        context['fiber_current_pages'] = self.get_fiber_current_pages()
        return context

    def get_template_names(self):
        if self.get_fiber_page() and self.get_fiber_page().template_name not in [None, '']:
            return self.get_fiber_page().template_name
        else:
            return DEFAULT_TEMPLATE

    def render_to_response(self, *args, **kwargs):
        if self.get_fiber_page() == None:
            """
            Take care of Django's CommonMiddleware redirect if the request URL doesn't end in a slash, and APPEND_SLASH=True
            https://docs.djangoproject.com/en/dev/ref/settings/#append-slash
            """
            url = self.get_fiber_page_url()

            if not url.endswith('/') and settings.APPEND_SLASH:
                return HttpResponsePermanentRedirect('%s/' % url)
            else:
                raise Http404
        else:
            """
            Block access to pages that the current user isn't supposed to see.
            """
            if not self.get_fiber_page().is_public_for_user(self.request.user):
                raise Http404

            if self.get_fiber_page().redirect_page and self.get_fiber_page().redirect_page != self.get_fiber_page(): #prevent redirecting to itself
                return HttpResponsePermanentRedirect(self.get_fiber_page().redirect_page.get_absolute_url())

        return super(FiberTemplateView, self).render_to_response(*args, **kwargs)

page = FiberTemplateView.as_view()
