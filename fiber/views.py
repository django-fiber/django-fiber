from django.conf import settings
from django.core.xheaders import populate_xheaders
from django.http import HttpResponse, HttpResponsePermanentRedirect, Http404
from django.template import loader, RequestContext

from app_settings import DEFAULT_TEMPLATE
from models import Page


def page(request):
    url = request.path_info

    context = RequestContext(request)
    if 'fiber_page' not in context:
        """
        Take care of Django's CommonMiddleware redirect if the request URL doesn't end in a slash, and APPEND_SLASH=True
        https://docs.djangoproject.com/en/dev/ref/settings/#append-slash
        """
        if not url.endswith('/') and settings.APPEND_SLASH:
            return HttpResponsePermanentRedirect('%s/' % url)
        else:
            raise Http404
    else:
        page = context['fiber_page']
        if page.redirect_page and page.redirect_page != page: #prevent redirecting to itself
            return HttpResponsePermanentRedirect(page.redirect_page.get_absolute_url())

    t = loader.get_template(page.template_name or DEFAULT_TEMPLATE)
    context['page'] = page

    response = HttpResponse(t.render(context))
    populate_xheaders(request, response, Page, page.id)
    return response
