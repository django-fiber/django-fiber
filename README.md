[travis-url]: http://travis-ci.org/#!/ridethepony/django-fiber
[travis-build-image]: https://secure.travis-ci.org/ridethepony/django-fiber.png

[pypi-url]: https://pypi.python.org/pypi/django-fiber/
[pypi-image]: https://pypip.in/d/django-fiber/badge.png

[coveralls-url]: https://coveralls.io/r/ridethepony/django-fiber
[coveralls-image]: https://coveralls.io/repos/ridethepony/django-fiber/badge.png?branch=master

[![Travis build image][travis-build-image]][travis-url]
[![PyPi download count image][pypi-image]][pypi-url]
[![Coverage Status][coveralls-image]][coveralls-url]

# Django Fiber

Do you want to see a Django Fiber screencast, to get a feel for what it can do for you? Check it out here:
http://vimeo.com/ridethepony/django-fiber

Or, if you want to quickly try out Django Fiber on your machine, install the Django Fiber example project:
https://github.com/ridethepony/django-fiber-example

Convinced? Want to use Django Fiber in your own Django project? Then follow the instructions below:


## Installation

We're assuming you are using Django 1.4, 1.5 or 1.6.

    $ pip install django-fiber


## Requirements

These dependencies are automatically installed:

    Pillow==2.2.1
    django-mptt==0.6.0
    django_compressor==1.3
    djangorestframework==2.3.8
    easy-thumbnails==1.4


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
        'easy_thumbnails',
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

[![Analytics](https://ga-beacon.appspot.com/UA-24341330-5/django-fiber/readme)](https://github.com/ridethepony/django-fiber)
