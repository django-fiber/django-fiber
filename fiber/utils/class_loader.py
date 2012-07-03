from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module


def load_class(fqc, **kwds):
    """ Load a class by its fully qualified classname and return an instance of it. """
    try:
        mod_name, klass_name = fqc.rsplit('.', 1)
        mod = import_module(mod_name)
    except ImportError, e:
        raise ImproperlyConfigured(('Error importing module {0}: "{1}"'.format(mod_name, e)))
    try:
        klass = getattr(mod, klass_name)
    except AttributeError:
        raise ImproperlyConfigured(('Module "{0}" does not define a "{1}" class'.format(mod_name, klass_name)))
    return klass(**kwds)
