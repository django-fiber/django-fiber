from django.conf import settings
from django.http import HttpResponsePermanentRedirect, Http404
from django.views.generic.base import TemplateView

from .app_settings import DEFAULT_TEMPLATE
from .mixins import FiberPageMixin


class FiberTemplateView(FiberPageMixin, TemplateView):

    def get_fiber_page_url(self):
        return self.request.path_info

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

            if self.get_fiber_page().redirect_page and self.get_fiber_page().redirect_page != self.get_fiber_page():  # prevent redirecting to itself
                return HttpResponsePermanentRedirect(self.get_fiber_page().redirect_page.get_absolute_url())

        return super(FiberTemplateView, self).render_to_response(*args, **kwargs)

page = FiberTemplateView.as_view()
