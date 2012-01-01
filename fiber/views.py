from django.conf import settings
from django.core.xheaders import populate_xheaders
from django.http import HttpResponse, HttpResponsePermanentRedirect, Http404
from django.template import loader, RequestContext
from django.views.decorators.csrf import csrf_protect

from app_settings import DEFAULT_TEMPLATE, ENABLE_I18N, I18N_PREFIX_MAIN_LANGUAGE
from models import Page


# This view is called from PageFallbackMiddleware.process_response
# when a 404 is raised, which often means CsrfViewMiddleware.process_view
# has not been called even if CsrfViewMiddleware is installed. So we need
# to use @csrf_protect, in case the template needs {% csrf_token %}.

@csrf_protect
def page(request, url):
    if ENABLE_I18N and I18N_PREFIX_MAIN_LANGUAGE and url in ('', '/'):
        return HttpResponsePermanentRedirect('%s/' % settings.LANGUAGE_CODE)

    if not url.endswith('/') and settings.APPEND_SLASH:
        return HttpResponsePermanentRedirect('%s/' % request.path)

    context = RequestContext(request)
    if 'fiber_page' not in context:
        raise Http404
    else:
        page = context['fiber_page']
        if page.redirect_page and page.redirect_page != page: #prevent redirecting to itself
            return HttpResponsePermanentRedirect(page.redirect_page.get_absolute_url())

    t = loader.get_template(page.template_name or DEFAULT_TEMPLATE)
    c = RequestContext(request, {'page': page,})

    response = HttpResponse(t.render(c))
    populate_xheaders(request, response, Page, page.id)
    return response
