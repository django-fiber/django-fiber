from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import path
from django.views.generic import View

from fiber.models import Page
from fiber.utils.validators import FiberURLValidator


class TestView(View):
    pass


urlpatterns = [
    path('test_url/', TestView.as_view(), name='another_named_url'),
]


@override_settings(ROOT_URLCONF=__name__)
class TestUtilsURLValidator(TestCase):
    validator = FiberURLValidator()

    def test_passes_normal(self):
        self.assertEqual(self.validator('http://www.google.com/'), None)

    def test_passes_url_contains_anchor(self):
        self.assertEqual(self.validator('/some/page/#SomeAnchor'), None)

    def test_passes_url_contains_querystring_and_anchor(self):
        self.assertEqual(self.validator('/some/page/?id=12&user_id=1#SomeAnchor'), None)

    def test_named_url(self):
        # Must raise if named url does not exist
        with self.assertRaises(ValidationError):
            self.validator('"some_named_url"')

        # Named url does exist
        self.assertEqual(self.validator('"another_named_url"'), None)

        # A fiber page also uses that named_url
        Page.objects.create(title='some_page', url='"another_named_url"').save()
        self.assertEqual(self.validator('"another_named_url"'), None)
