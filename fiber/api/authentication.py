from django.http import HttpResponse
from django.utils.importlib import import_module
from django.conf import settings


class DjangoStaffAuthentication(object):
    """
    Django staff authentication for Django Piston
    """
    def __init__(self):
        pass

    def is_authenticated(self, request):
        """
        This method calls the `is_authenticated` and `is_staff`
        method of request.user.

        `is_authenticated`: Will be called when checking for
        authentication. It returns True if the user is authenticated
        and is a staff member.
        """
        self.request = request
        return request.user.is_authenticated and request.user.is_staff

    def challenge(self):
        """
        `challenge`: In cases where `is_authenticated` returns
        False, the result of this method will be returned.
        This will usually be a `HttpResponse` object with
        some kind of challenge headers and 401 code on it.
        """
        response = HttpResponse()
        response.status_code = 401

        return response
