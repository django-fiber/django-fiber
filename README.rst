Django Fiber
============

An important message from the creators
--------------------------------------

Hi Django Fiber enthusiasts! This is a message from the people at Ride The Pony, Leukeleu and Jouw Omgeving. We started Django Fiber in 2011, because we felt that there wasn't a good, *simple* Django CMS available. Lots of people felt the same, which was why Django Fiber was pretty popular back then. And it is still going strong in lots of sites, so we hear :)

We have used Django Fiber ourselves in over 100 websites and web applications. But a new contender has stepped up. Django Fiber has finally met its match, and it is called `Wagtail <https://wagtail.io/>`_.
In the last couple of projects we started using Wagtail, and we really like it a lot. If we're totally honest we have to admit that we even like it better than our own creation. If this happens you know it's time to move on.

But we can't let you (and our clients, ahem...) get stuck on an old version of Django Fiber, that is not compatible with the latest and greatest in wonderful Django-land, now can we? That's why we buckled down, and brought Django Fiber into 2017. What you see here is the result: this (final?) version of Django Fiber works with Django 1.8, 1.9 and 1.10, has up-to-date requirements, and can even run on Python 3.

We hope you're happy with this latest push, but we can also imagine that you're a little sad (we are!) that Django Fiber is moving into its retirement home.
If you think that Django Fiber has a lot more to give, we are more than welcome to give you a commit bit to this repository, so you can 'make Django Fiber great again' (pun totally intended).

Join the discussion about this development in issue #244

The guys and gals at Ride The Pony, Leukeleu and Jouw Omgeving


|Travis build image| |PyPI version| |Coverage Status|

Do you want to see a Django Fiber screencast, to get a feel for what  it can do
for you? `Check it out on Vimeo <http://vimeo.com/ridethepony/django-fiber>`_

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

We're assuming you are using Django 1.8-1.10. Then simply install Fiber
using pip::

    $ pip install django-fiber



Setup
~~~~~

Open **settings.py** and add the following to your INSTALLED_APPS

::

   INSTALLED_APPS = (
        ...
        'mptt',
        'compressor',
        'easy_thumbnails',
        'fiber',
        ...
   )

Add Fiber to the MIDDLEWARE_CLASSES list

::

    import django.conf.global_settings as DEFAULT_SETTINGS

    MIDDLEWARE_CLASSES = DEFAULT_SETTINGS.MIDDLEWARE_CLASSES + (
        ...
        'fiber.middleware.ObfuscateEmailAddressMiddleware',
        'fiber.middleware.AdminPageMiddleware',
    )

Add the request context processor

::

    TEMPLATES = [
        {
            ...
            'OPTIONS': {
                'context_processors': [
                    ...
                    'django.template.context_processors.request',
                ]
            }
        },
    ]

And configure compressor

::

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    STATIC_URL = '/static/'
    STATICFILES_FINDERS = DEFAULT_SETTINGS.STATICFILES_FINDERS + [
        'compressor.finders.CompressorFinder',
    ]

Edit your **urls.py** to add the Fiber site to your url-patterns

::

    from django.conf.urls import include, url
    from fiber.views import page

    urlpatterns = [
        ...
        url(r'^api/v2/', include('fiber.rest_api.urls')),
        url(r'^admin/fiber/', include('fiber.admin_urls')),
        ...
        url(r'', page),
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

.. |Travis build image| image:: https://secure.travis-ci.org/ridethepony/django-fiber.svg?branch=master
   :target: http://travis-ci.org/#!/ridethepony/django-fiber
.. |PyPI version| image:: https://img.shields.io/pypi/v/django-fiber.svg
   :target: https://pypi.python.org/pypi/django-fiber/
.. |Coverage Status| image:: https://coveralls.io/repos/ridethepony/django-fiber/badge.svg?branch=master
   :target: https://coveralls.io/r/ridethepony/django-fiber
.. |Analytics| image:: https://ga-beacon.appspot.com/UA-24341330-5/django-fiber/readme
   :target: https://github.com/ridethepony/django-fiber
