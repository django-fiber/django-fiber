import re

from django.core.exceptions import ImproperlyConfigured

from .models import Page


class FiberPageMixin(object):
    """
    Adds fiber_page and fiber_current_pages to the context
    """
    fiber_page_url = None
    fiber_page = None
    fiber_current_pages = None

    def get_context_data(self, **kwargs):
        context = super(FiberPageMixin, self).get_context_data(**kwargs)
        context['fiber_page'] = self.get_fiber_page()
        context['fiber_current_pages'] = self.get_fiber_current_pages()
        return context

    def get_fiber_page_url(self):
        if not self.fiber_page_url:
            raise ImproperlyConfigured(u"{cls} is missing a fiber_page_url. Define "
                u"{cls}.fiber_page_url, or override "
                u"{cls}.get_fiber_page_url().".format(cls=self.__class__.__name__)
            )
        return self.fiber_page_url

    def get_fiber_page(self):
        return self.fiber_page or Page.objects.get_by_url(self.get_fiber_page_url())

    def get_fiber_current_pages(self):
        if self.fiber_current_pages is None:
            current_pages = []
            """
            Find pages that should be marked as current in menus.
            """
            current_page = self.get_fiber_page()
            if current_page:
                """
                The current page should be marked as current, obviously,
                as well as all its ancestors.
                """
                current_pages.append(current_page)
                current_pages.extend(current_page.get_ancestors())

            """
            For all pages that are not already current_pages,
            check if one of the `mark_current_regexes` matches the requested URL.
            If so, add the page and all its ancestors to the current_pages list.
            """
            current_page_candidates = Page.objects.exclude(mark_current_regexes__exact='')
            url = self.get_fiber_page_url()

            for candidate in list(set(current_page_candidates) - set(current_pages)):
                for mark_current_regex in candidate.mark_current_regexes.strip().splitlines():
                    if re.match(mark_current_regex, url):
                        current_pages.append(candidate)
                        current_pages.extend(candidate.get_ancestors())
                        break

            """
            Order current_pages for use with tree_info template tag,
            and remove the root node in the process.
            """
            current_pages = sorted(current_pages, key=lambda fiber_current_page: fiber_current_page.lft)[1:]

        return current_pages
