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

We're assuming you are using Django 1.3. If you need to install Django Fiber with an older Django version, you can find instructions in the docs folder.

::

	$ pip install django-fiber


Requirements:
=============

These dependencies are automatically installed:

::

	PIL>=1.1.7
	django-piston==0.2.3rc1
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
	    'fiber.context_processors.page_info',
	)

	INSTALLED_APPS = (
	    ...
	    'django.contrib.staticfiles',
	    'piston',
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
	    (r'^api/v1/', include('fiber.api.urls')),
	    (r'^admin/fiber/', include('fiber.admin_urls')),
	    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {'packages': ('fiber',),}),
	    ...
	    (r'', 'fiber.views.page'),
	)

	if settings.DEBUG:
	    urlpatterns += patterns('django.contrib.staticfiles.views',
	        url(r'^static/(?P<path>.*)$', 'serve'),
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
