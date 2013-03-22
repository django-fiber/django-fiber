[![Travis build image][travis-build-image]][travis]

[travis]: http://travis-ci.org/#!/ridethepony/django-fiber
[travis-build-image]: https://secure.travis-ci.org/ridethepony/django-fiber.png

# Django Fiber

---

**Announcement**: We've upgraded to Django REST Framework 2. This means that if you want to use the latest
Fiber and you use Django REST Framework 0.3.X or 0.4.X for your own project, you'll have to bite the bullet and upgrade your local REST Framework code.

---

Do you want to see a Django Fiber screencast, to get a feel for what it can do for you? Check it out here:
http://vimeo.com/ridethepony/django-fiber

Or, if you want to quickly try out Django Fiber on your machine, install the Django Fiber example project:
https://github.com/ridethepony/django-fiber-example

Convinced? Want to use Django Fiber in your own Django project? Then follow the instructions below:


## Installation

We're assuming you are using Django 1.3.x, 1.4 or 1.5.

    $ pip install django-fiber


## Requirements

These dependencies are automatically installed:

    Pillow==1.7.8
    django-mptt==0.5.5
    django-compressor>=1.2
    djangorestframework==2.1.17


## Settings

### settings.py

    import django.conf.global_settings as DEFAULT_SETTINGS

    MIDDLEWARE_CLASSES = DEFAULT_SETTINGS.MIDDLEWARE_CLASSES + (
        'fiber.middleware.ObfuscateEmailAddressMiddleware',
        'fiber.middleware.AdminPageMiddleware',
    )

    TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + (
        'django.core.context_processors.request',
    )

    INSTALLED_APPS = (
        ...
        'django.contrib.staticfiles',
        'mptt',
        'compressor',
        'fiber',
        ...
    )

    import os
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    STATIC_URL = '/static/'
    STATICFILES_FINDERS = DEFAULT_SETTINGS.STATICFILES_FINDERS + (
        'compressor.finders.CompressorFinder',
    )

### urls.py

    from django.conf import settings

    urlpatterns = patterns('',
        ...
        (r'^api/v2/', include('fiber.rest_api.urls')),
        (r'^admin/fiber/', include('fiber.admin_urls')),
        (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {'packages': ('fiber',),}),
        ...
        (r'', 'fiber.views.page'),
    )


## Post-installation

Create database tables:

    $ python manage.py syncdb

All static Fiber files need to be symlinked in (or copied to) your media folder:

    $ python manage.py collectstatic --link


## Further documentation
For further usage and configuration details take a look at our documentation project at [readthedocs](https://django-fiber.readthedocs.org/).

## Changelog
See CHANGELOG.md for the latest changes.

[changelog]: CHANGELOG.md
