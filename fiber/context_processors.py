import re

from app_settings import EXCLUDE_URLS
from models import Page
from utils.urls import get_named_url_from_quoted_url, is_quoted_url


def page_info(request):
    context = {}
    page = None
    current_pages = []

    url = request.path_info

    """
    Avoid further processing or database queries if page is in EXCLUDE_URLS.
    """
    if EXCLUDE_URLS:
        for exclude_url in EXCLUDE_URLS:
            if re.search(exclude_url, request.path.lstrip('/')):
                return context

    """
    Find Page that matches the requested URL.

    First check if there is a Page whose `url` matches the requested URL.
    """
    try:
        page = Page.objects.get(url__exact=url)
    except Page.DoesNotExist:
        pass

    """
    If no Page has been found, check a subset of Pages (whose `url` or
    `relative_url` contain the rightmost part of the requested URL), to see
    if their `get_absolute_url()` matches the requested URL entirely.
    """
    if not page:
        last_url_part = url.rstrip('/').rsplit('/', 1)[-1]
        if last_url_part:
            page_candidates = Page.objects.exclude(url__exact='', ) \
                .filter(url__icontains=last_url_part)
            if page_candidates:
                for page_candidate in page_candidates:
                    if page_candidate.get_absolute_url() == url:
                        page = page_candidate
                        break

    """
    If no Page has been found, try to find a Page by matching the
    requested URL with reversed `named_url`s.
    """
    if not page:
        page_candidates = Page.objects.exclude(url__exact='')
        if page_candidates:
            for page_candidate in page_candidates:
                if is_quoted_url(page_candidate.url):
                    if get_named_url_from_quoted_url(page_candidate.url) == url:
                        page = page_candidate
                        break

    """
    Block access to pages that the current user isn't supposed to see.
    """
    if request.user.is_authenticated():
        if page:
            if page not in Page.objects.visible_pages_for_user(request.user):
                page = None

    """
    Find pages that should be marked as current in menus.
    """
    if page:
        """
        The current page should be marked as current, obviously,
        as well as all its ancestors.
        """
        current_pages.append(page)
        current_pages.extend(page.get_ancestors())

    """
    For all pages that are not already current_pages,
    check if one of the `mark_current_regexes` matches the requested URL.
    If so, add the page and all its ancestors to the current_pages list.
    """
    current_page_candidates = Page.objects.exclude(mark_current_regexes__exact='')
    for current_page_candidate in list(set(current_page_candidates) - set(current_pages)):
        for mark_current_regex in current_page_candidate.mark_current_regexes.strip().splitlines():
            if re.match(mark_current_regex, url):
                current_pages.append(current_page_candidate)
                current_pages.extend(current_page_candidate.get_ancestors())
                break

    """
    Order current_pages for use with tree_info template tag,
    and remove the root node in the process.
    """
    current_pages = sorted(current_pages, key=lambda current_page: current_page.lft)[1:]

    if page:
        context['fiber_page'] = page

    if current_pages:
        context['fiber_current_pages'] = current_pages

    return context
