from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.utils.translation import ugettext as _

from models import Page, ContentItem


def fiber_login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)

    result = {}
    if user is not None:
        if user.is_active:
            login(request, user)
            result = {
                'status': 'success',
            }
        else:
            result = {
                'status': 'inactive',
                'message': _('This account is inactive.'),
            }
    else:
            result = {
                'status': 'failed',
                'message': _('Please enter a correct username and password. Note that both fields are case-sensitive.'),
            }
    json = simplejson.dumps(result)
    return HttpResponse(json, mimetype='application/json')


@staff_member_required
def page_move_up(request, id):
    page = Page.objects.get(pk=id)

    if page:
        previous_sibling_page = page.get_previous_sibling()
        if previous_sibling_page:
            page.move_to(previous_sibling_page, position='left')

    return HttpResponseRedirect('../../')


@staff_member_required
def page_move_down(request, id):
    page = Page.objects.get(pk=id)

    if page:
        next_sibling_page = page.get_next_sibling()
        if next_sibling_page:
            page.move_to(next_sibling_page, position='right')

    return HttpResponseRedirect('../../')


@staff_member_required
def pages_json(request):
    """
    Returns page tree as json. The data is suitable for jqtree.
    """
    return HttpResponse(
        simplejson.dumps(
            Page.objects.create_jqtree_data()
        )
    )
