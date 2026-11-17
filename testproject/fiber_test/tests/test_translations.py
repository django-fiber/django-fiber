"""Both gettext domains must remain available to Django."""

from django.test import RequestFactory, SimpleTestCase
from django.utils.translation import gettext, override
from django.views.i18n import JavaScriptCatalog


class TranslationLoadingTests(SimpleTestCase):
    def test_python_catalogue(self):
        with override('nl'):
            self.assertEqual(gettext('No reverse match found for the named url'),
                             "Geen 'reverse match' gevonden voor de 'named url'")

    def test_javascript_catalogue(self):
        with override('nl'):
            response = JavaScriptCatalog.as_view(packages=['fiber'])(RequestFactory().get('/jsi18n/'))
        self.assertContains(response, 'Toon ruwe JSON')
        self.assertContains(response, 'Upload nieuw bestand')
