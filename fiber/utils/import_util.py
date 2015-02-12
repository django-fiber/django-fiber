from django.core.exceptions import ImproperlyConfigured
try:
    from django.utils.module_loading import import_string
except ImportError:  # Django < 1.7
    import_string = None
try:
    from importlib import import_module
except ImportError:   # Python < 2.7 && Django < 1.6
    from django.utils.importlib import import_module


def import_element(path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImproperlyConfigured if the import failed.

    E.g:
      f = import_element('fiber.utils.import_util.import_element')
    """
    if import_string:
        try:
            return import_string(path)
        except ImportError as e:
            raise ImproperlyConfigured('Error importing %s: %s' % (path, e))
    else:  # Django < 1.7
        try:
            module_path, classname = path.rsplit('.', 1)
        except ValueError:
            msg = "%s doesn't look like a module path" % path
            raise ImproperlyConfigured('Error importing %s: %s' % (path, msg))

        try:
            module = import_module(module_path)
        except ImportError as e:
            raise ImproperlyConfigured('Error importing %s: %s' % (path, e))

        try:
            return getattr(module, classname)
        except AttributeError:
            msg = 'Module "%s" does not define a "%s" attribute/class' % (path, classname)
            raise ImproperlyConfigured('Error importing %s: %s' % (path, msg))


def load_class(path, **kwds):
    """ Load a class by its fully qualified classname and return an instance of it. """
    klass = import_element(path)
    return klass(**kwds)
