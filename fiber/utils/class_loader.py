from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured


def load_class(fqc, **kwds):
    """ Load a class by its fully qualified classname and return an instance of it. """
    try:
        mod_name, klass_name = fqc.rsplit('.', 1)
        mod = import_module(mod_name)
    except ImportError, e:
        raise ImproperlyConfigured(('Error importing email backend module %s: "%s"'
                                    % (mod_name, e)))
    try:
        klass = getattr(mod, klass_name)
    except AttributeError:
        raise ImproperlyConfigured(('Module "%s" does not define a '
                                    '"%s" class' % (mod_name, klass_name)))
    return klass(**kwds)
