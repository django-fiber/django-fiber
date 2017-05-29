import django
from django.test import RequestFactory
from django.http import HttpResponse


class TestNewStyleMiddlewareMixin(object):
    middleware_factory = NotImplemented

    if django.VERSION >= (1, 10):
        def test_new_style(self):
            def get_response(request):
                return HttpResponse('Test')
            request = RequestFactory().get('/')

            callable_middleware = self.middleware_factory(get_response)
            self.assertEqual(callable_middleware(request).content,
                             'Test')
