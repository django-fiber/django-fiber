.. image:: https://secure.travis-ci.org/ridethepony/django-fiber.png
  :target: http://travis-ci.org/#!/ridethepony/django-fiber

============
Django Fiber
============

Do you want to see a Django Fiber screencast, to get a feel for what it can do for you? Check it out here:
http://vimeo.com/ridethepony/django-fiber

Or, if you want to quickly try out Django Fiber on your machine, install the Django Fiber example project:
https://github.com/ridethepony/django-fiber-example

Convinced? Want to use Django Fiber in your own Django project? Then follow the instructions below:


Installation:
=============

We're assuming you are using Django 1.3.x or 1.4.

::

	$ pip install django-fiber


Requirements:
=============

These dependencies are automatically installed:

::

	Pillow==1.7.7
	djangorestframework==0.3.3
	django-mptt==0.5.1
	django-compressor>=0.7.1


Settings:
=========

settings.py
-----------

::

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
	    'djangorestframework',
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

urls.py
-------

::

	from django.conf import settings

	urlpatterns = patterns('',
	    ...
	    (r'^api/v2/', include('fiber.rest_api.urls')),
	    (r'^admin/fiber/', include('fiber.admin_urls')),
	    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {'packages': ('fiber',),}),
	    ...
	    (r'', 'fiber.views.page'),
	)


Post-installation:
==================

Create database tables::

	$ python manage.py syncdb

All static Fiber files need to be symlinked in (or copied to) your media folder::

	$ python manage.py collectstatic --link


Further documentation:
======================

You can find usage instructions, and other documentation, in the docs folder.
