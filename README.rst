Django Fiber
============

|Travis build image| |PyPI version| |Coverage Status|

Do you want to see a Django Fiber screencast, to get a feel for what  it can do
for you? `Check it out on Vimeo <http://vimeo.com/ridethepony/django-fiber>`_

Convinced? Want to use Django Fiber in your own Django project? Then follow the
instructions below.

Installation
------------

We're assuming you are using Django 1.8-1.10. Then simply install Fiber
using pip::

    $ pip install django-fiber

Requirements
------------

These dependencies are automatically installed::

    Pillow>=2.2.1
    django-mptt>=0.8
    django_compressor>=2.0
    djangorestframework>=3.4
    easy-thumbnails>=2.2

Settings
--------

settings.py
~~~~~~~~~~~

::

    import django.conf.global_settings as DEFAULT_SETTINGS

    MIDDLEWARE_CLASSES = DEFAULT_SETTINGS.MIDDLEWARE_CLASSES + (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'fiber.middleware.ObfuscateEmailAddressMiddleware',
        'fiber.middleware.AdminPageMiddleware',
    )

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    ...
                    'django.template.context_processors.request',
                ]
            }
        },
    ]


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

urls.py
~~~~~~~

::

    from django.conf import settings

    urlpatterns = [
        ...
        url(r'^api/v2/', include('fiber.rest_api.urls')),
        url(r'^admin/fiber/', include('fiber.admin_urls')),
        ...
        url(r'', fiber.views.page),
    ]

Post-installation
-----------------

Create database tables::

    $ python manage.py migrate

All static Fiber files need to be symlinked in (or copied to) your media
folder::

    $ python manage.py collectstatic --link

Further documentation
---------------------

For further usage and configuration details take a look at our
documentation project at
`readthedocs <https://django-fiber.readthedocs.org/>`__.

Changelog
---------

See `CHANGELOG.md <https://github.com/ridethepony/django-fiber/blob/master/CHANGELOG.md>`_
for the latest changes.

|Analytics|

.. |Travis build image| image:: https://secure.travis-ci.org/ridethepony/django-fiber.svg?branch=dev
   :target: http://travis-ci.org/#!/ridethepony/django-fiber
.. |PyPI version| image:: https://img.shields.io/pypi/v/django-fiber.svg
   :target: https://pypi.python.org/pypi/django-fiber/
.. |Coverage Status| image:: https://coveralls.io/repos/ridethepony/django-fiber/badge.svg?branch=dev
   :target: https://coveralls.io/r/ridethepony/django-fiber
.. |Analytics| image:: https://ga-beacon.appspot.com/UA-24341330-5/django-fiber/readme
   :target: https://github.com/ridethepony/django-fiber
