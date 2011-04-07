from django.utils.importlib import import_module
from django.core import exceptions


def import_element(path):
    """
    Import element in a module.

    E.g:
      f = import_element('fiber.utils.import_util.import_element')
    """
    try:
        dot = path.rindex('.')
    except ValueError:
        raise exceptions.ImproperlyConfigured('%s isn\'t a valid module' % path)

    module_path, classname = path[:dot], path[dot+1:]

    try:
        module = import_module(module_path)
    except ImportError, e:
        raise exceptions.ImproperlyConfigured('Error importing module %s: "%s"' % (module_path, e))

    try:
        return getattr(module, classname)
    except AttributeError:
        raise exceptions.ImproperlyConfigured('Module "%s" does not define a "%s" class' % (module_path, classname))
