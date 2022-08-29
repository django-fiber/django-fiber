Django Fiber
============

|Build image| |PyPI version| |Coverage Status|

An important message about this project
---------------------------------------

Hi Django Fiber enthusiasts! This project was started by the people at Ride The Pony, Leukeleu and Jouw Omgeving.
They started Django Fiber in 2011, because they wanted a good, *simple* Django CMS available. Lots of people felt the
same, which was why Django Fiber became pretty popular. And it is still going strong in lots of sites, so we hear :)

Later, they discovered `Wagtail <https://wagtail.io/>`_, and found it to be even better than their own creation. So
they decided to move on. Nevertheless, Django Fiber was popular, used in many websites, and they didn't want to just
drop it. At the start of 2017 they handed over control of the project to a new group of maintainers - the discussion
about this handover can be found in `issue #244 <https://github.com/django-fiber/django-fiber/issues/244>`_.

Currently Django Fiber is in 'maintenance mode'. What this means it that it will be updated to run with the
latest releases of Django - and of other packages that Django Fiber depends on. However, no effort will be made to
add new features.

If a user really wants a new feature added - then a well-written PR will be reviewed and considered. But other than
that, Django Fiber is staying exactly as it is :)

About Django Fiber
------------------

Do you want to see a Django Fiber screencast, to get a feel for what  it can do
for you? `Check it out on Vimeo <https://vimeo.com/24678409>`_

Convinced? Want to use Django Fiber in your own Django project? Then follow the
instructions below.

Requirements
------------

These dependencies are automatically installed::

    Pillow>=2.2.1
    django-mptt>=0.8
    django_compressor>=2.0
    djangorestframework>=3.4
    easy-thumbnails>=2.2

Installation
------------

We're assuming you are using Django 1.9-2.0. Then simply install Fiber
using pip::

    $ pip install django-fiber



Setup
~~~~~

Open **settings.py** and add the following to your INSTALLED_APPS

.. code-block:: python

   INSTALLED_APPS = (
        'mptt',
        'compressor',
        'easy_thumbnails',
        'fiber',
        ...
   )

Add Fiber to the MIDDLEWARE_CLASSES list

.. code-block:: python

    import django.conf.global_settings as DEFAULT_SETTINGS

    MIDDLEWARE_CLASSES = DEFAULT_SETTINGS.MIDDLEWARE_CLASSES + (
        'fiber.middleware.ObfuscateEmailAddressMiddleware',
        'fiber.middleware.AdminPageMiddleware',
        ...
    )

(Or, add the same items to ``MIDDLEWARE`` if you are using Django 1.10 or later.)

Add the request context processor

.. code-block:: python

    TEMPLATES = [
        {
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.request',
                    ...
                ]
            }
            ...
        },
    ]

And configure compressor

.. code-block:: python

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    STATIC_URL = '/static/'
    STATICFILES_FINDERS = DEFAULT_SETTINGS.STATICFILES_FINDERS + [
        'compressor.finders.CompressorFinder',
    ]

Edit your **urls.py** to add the Fiber site to your url-patterns

.. code-block:: python

    from django.urls import include, path, re_path
    from fiber.views import page

    urlpatterns = [
        ...
        path('api/v2/', include('fiber.rest_api.urls')),
        path('admin/fiber/', include('fiber.admin_urls')),
        ...
        re_path('', page),
    ]

Post-installation
-----------------

Create database tables::

    $ python manage.py migrate

All static Fiber files need to be symlinked in (or copied to) your static files folder if you're not on your dev machine::

    $ python manage.py collectstatic --link

Further documentation
---------------------

For further usage and configuration details take a look at our
documentation project at
`readthedocs <https://django-fiber.readthedocs.org/>`__.

Changelog
---------

See `CHANGELOG.md <https://github.com/django-fiber/django-fiber/blob/master/CHANGELOG.rst>`_
for the latest changes.

.. |Build image| image:: https://github.com/django-fiber/django-fiber/workflows/CI/badge.svg?branch=master
     :target: https://github.com/django-fiber/django-fiber/actions?workflow=CI
     :alt: CI Status
.. |PyPI version| image:: https://img.shields.io/pypi/v/django-fiber.svg
   :target: https://pypi.python.org/pypi/django-fiber/
.. |Coverage Status| image:: https://codecov.io/github/django-fiber/django-fiber/coverage.svg?branch=master
    :target: https://codecov.io/github/django-fiber/django-fiber?branch=master
