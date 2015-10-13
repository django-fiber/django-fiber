import warnings
from fiber.mixins import FiberPageMixin

warnings.warn('NOTE: the page_info context processor is deprecated and will be removed in the near future.', DeprecationWarning)

import re

from .app_settings import EXCLUDE_URLS


class FiberPageContext(FiberPageMixin):
    def __init__(self, request):
        self.request = request
        self.fiber_page_url = request.path_info

    def get_fiber_page(self):
        page = super(FiberPageContext, self).get_fiber_page()
        # Block access to pages that the current user isn't supposed to see.
        if page and not page.is_public_for_user(self.request.user):
            page = None
        return page


def page_info(request):
    context = FiberPageContext(request)

    if EXCLUDE_URLS:
        for exclude_url in EXCLUDE_URLS:
            if re.search(exclude_url, context.get_fiber_page_url().lstrip('/')):
                return {}

    return context.get_context_data()
