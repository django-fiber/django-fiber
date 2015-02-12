from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from fiber.utils.import_util import import_element


class TestImportUtil(SimpleTestCase):
    def test_import_element(self):
        """Import this class by name"""
        path = '.'.join([self.__module__, self.__class__.__name__])
        self.assertEqual(import_element(path), self.__class__)

    def test_import_module_raises_improperly_configured(self):
        """We can only import attributes from modules, not modules directly"""
        with self.assertRaises(ImproperlyConfigured) as cm:
            import_element('fiber')
        self.assertEqual(str(cm.exception), 'Error importing fiber: fiber doesn\'t look like a module path')

    def test_import_invalid_module_raises_improperly_configured(self):
        """Fail trying to import a missing module"""
        with self.assertRaises(ImproperlyConfigured) as cm:
            import_element('fiber.missing_module.missing_attribute')
        self.assertEqual(str(cm.exception), 'Error importing fiber.missing_module.missing_attribute: No module named missing_module')

    def test_import_invalid_attribute_raises_improperly_configured(self):
        """Fail trying to import a missing attribute"""
        with self.assertRaises(ImproperlyConfigured) as cm:
            import_element('fiber.missing_attribute')
        self.assertEqual(str(cm.exception), 'Error importing fiber.missing_attribute: Module "fiber.missing_attribute" does not define a "missing_attribute" attribute/class')
