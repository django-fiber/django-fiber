import re

from app_settings import EXCLUDE_URLS
from models import Page


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
            if re.search(exclude_url, url.lstrip('/')):
                return context

    page = Page.objects.get_by_url(url)

    """
    Block access to pages that the current user isn't supposed to see.
    """
    if page:
        if not page.is_public_for_user(request.user):
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
