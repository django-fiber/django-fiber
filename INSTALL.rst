===============================================
Installation instructions for Django 1.3 or 1.4
===============================================


Installation:
=============

We're assuming you are using Django 1.3 or 1.4. If you need to install Django Fiber with an older Django version, you can find instructions in the docs folder.

::

	$ pip install django-fiber


Requirements:
=============

These dependencies are automatically installed:

::

	Pillow==1.7.7
    djangorestframework==0.3.3
	django-mptt>=0.4.2
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


Documentation:
==============

You can find usage instructions, and other documentation, in the docs folder.
