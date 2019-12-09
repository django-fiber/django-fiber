from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from fiber.utils.import_util import import_element, load_class


class TestClass:
    def __init__(self, foo=None):
        self.foo = foo


class TestImportUtil(SimpleTestCase):
    def test_import_element(self):
        """Import TestClass by name"""
        path = '.'.join([self.__module__, 'TestClass'])
        self.assertEqual(import_element(path), TestClass)

    def test_import_module_raises_improperly_configured(self):
        """We can only import attributes from modules, not modules directly"""
        with self.assertRaises(ImproperlyConfigured) as cm:
            import_element('fiber')
        self.assertEqual(str(cm.exception), 'Error importing fiber: fiber doesn\'t look like a module path')

    def test_import_invalid_module_raises_improperly_configured(self):
        """Fail trying to import a missing module"""
        with self.assertRaises(ImproperlyConfigured) as cm:
            import_element('fiber.missing_module.missing_attribute')
        self.assertRegex(str(cm.exception),
                         r'Error importing fiber.missing_module.missing_attribute: No module named .+')

    def test_import_invalid_attribute_raises_improperly_configured(self):
        """Fail trying to import a missing attribute"""
        with self.assertRaises(ImproperlyConfigured) as cm:
            import_element('fiber.missing_attribute')
        msgs = [
            'Error importing fiber.missing_attribute: Module "fiber.missing_attribute" does not define a "missing_attribute" attribute/class',
            'Error importing fiber.missing_attribute: Module "fiber" does not define a "missing_attribute" attribute/class',
            # Django 1.8 and later
        ]
        self.assertIn(str(cm.exception), msgs)

    def test_load_class(self):
        """Import and instantiate TestClass by name"""
        path = '.'.join([self.__module__, 'TestClass'])
        self.assertIsInstance(load_class(path), TestClass)

    def test_load_class_with_kwargs(self):
        """Import and instantiate TestClass by name with kwargs"""
        path = '.'.join([self.__module__, 'TestClass'])
        instance = load_class(path, foo='bar')
        self.assertEqual(instance.foo, 'bar')
