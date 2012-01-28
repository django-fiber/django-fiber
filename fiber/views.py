from django.conf import settings
from django.core.xheaders import populate_xheaders
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, Http404
from django.template import loader, RequestContext

from app_settings import DEFAULT_TEMPLATE, ENABLE_I18N, I18N_PREFIX_MAIN_LANGUAGE
from models import Page

def page(request):
    url = request.path_info

    if ENABLE_I18N and I18N_PREFIX_MAIN_LANGUAGE and url in ('', '/'):
        return HttpResponseRedirect('%s/' % settings.LANGUAGE_CODE)

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
