from django.conf import settings
from django.http import HttpResponsePermanentRedirect, Http404
from django.views.generic.base import TemplateView

from .app_settings import DEFAULT_TEMPLATE
from .mixins import FiberPageMixin


class FiberTemplateView(FiberPageMixin, TemplateView):

    def get_fiber_page_url(self):
        return self.request.path_info

    def get_template_names(self):
        if self.get_fiber_page() and self.get_fiber_page().template_name:
            return self.get_fiber_page().template_name
        else:
            return DEFAULT_TEMPLATE

    def render_to_response(self, *args, **kwargs):
        fiber_page = self.get_fiber_page()
        if fiber_page is None:
            url = self.get_fiber_page_url()
            # Redirect if the request URL doesn't end in a slash, and APPEND_SLASH=True (https://docs.djangoproject.com/en/dev/ref/settings/#append-slash)
            if not url.endswith('/') and settings.APPEND_SLASH:
                return HttpResponsePermanentRedirect('%s/' % url)
            else:
                raise Http404
        else:
            # Block access to pages the current user isn't supposed to see
            if not fiber_page.is_public_for_user(self.request.user):
                raise Http404

            if fiber_page.redirect_page and fiber_page.redirect_page != fiber_page:  # prevent redirecting to itself
                return HttpResponsePermanentRedirect(fiber_page.redirect_page.get_absolute_url())

        return super().render_to_response(*args, **kwargs)

page = FiberTemplateView.as_view()
