from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string


def import_element(path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImproperlyConfigured if the import failed.

    E.g:
      f = import_element('fiber.utils.import_util.import_element')
    """
    try:
        return import_string(path)
    except ImportError as e:
        raise ImproperlyConfigured(f'Error importing {path}: {e}')


def load_class(path, **kwds):
    """ Load a class by its fully qualified classname and return an instance of it. """
    klass = import_element(path)
    return klass(**kwds)
