from django.conf.urls import patterns, url
from django.views.generic import View
from django.core.exceptions import ValidationError
from django.test import TestCase

from fiber.utils.validators import FiberURLValidator
from fiber.models import Page


class TestView(View):
    pass


class TestUtilsURLValidator(TestCase):
    urls = patterns('',
        url(r'^test_url/$', TestView.as_view(), name='another_named_url'),
    )  # use this url conf for our tests
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
        self.assertEquals(self.validator('"another_named_url"'), None)

        # A fiber page also uses that named_url
        Page.objects.create(title='some_page', url='"another_named_url"').save()
        self.assertEquals(self.validator('"another_named_url"'), None)
