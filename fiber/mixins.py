import re
from operator import attrgetter

from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_str

from .models import Page


class FiberPageMixin:
    """
    Adds fiber_page and fiber_current_pages to the context
    """
    # This attribute must be set in the subclass
    fiber_page_url = None

    # These attributes may be overridden in a subclass
    fiber_page = None
    fiber_current_pages = None

    def get_context_data(self, **kwargs):
        super_obj = super()
        if hasattr(super_obj, 'get_context_data'):
            context = super_obj.get_context_data(**kwargs)
        else:
            context = {}
            context.update(kwargs)
        if self.get_fiber_page():
            context.update({
                'fiber_page': self.get_fiber_page(),
                'fiber_current_pages': self.get_fiber_current_pages()
            })
        return context

    def get_fiber_page_url(self):
        if not self.fiber_page_url:
            raise ImproperlyConfigured(
                '{mod}.{cls} is missing a fiber_page_url. Define {cls}.fiber_page_url,'
                ' or override {cls}.get_fiber_page_url().'.format(mod=self.__module__, cls=self.__class__.__name__))
        return self.fiber_page_url

    def get_fiber_page(self):
        if self.fiber_page is None:
            self.fiber_page = Page.objects.get_by_url(self.get_fiber_page_url())
        return self.fiber_page

    def get_fiber_current_pages(self):
        """
        Find pages that should be marked as current in menus.
        """
        if not self.fiber_current_pages:  # None or empty list
            current_pages = set()
            current_page = self.get_fiber_page()
            if current_page:
                # Mark the current page and its ancestors as current
                current_pages = set([current_page] + list(current_page.get_ancestors()))

            # Find all pages that are not already current_pages and have mark_current_regexes configured
            candidates = Page.objects.exclude(pk__in=map(attrgetter('pk'), current_pages)).exclude(mark_current_regexes__exact='')
            url = force_str(self.get_fiber_page_url())

            for candidate in candidates:
                # Check if one of the mark_current_regexes matches the requested URL.
                for mark_current_regex in candidate.mark_current_regexes.strip().splitlines():
                    if re.match(mark_current_regex.strip(), url):
                        # Mark this page and its ancestors as current
                        current_pages.update([candidate] + list(candidate.get_ancestors()))
                        break

            # Order current_pages for use with tree_info template tag, remove the root page in the process.
            self.fiber_current_pages = sorted(current_pages, key=attrgetter('lft'))[1:]

        return self.fiber_current_pages
