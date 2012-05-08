==========================================
Installation instructions for Django 1.2.x
==========================================


Installation:
=============

These are the installation instructions for Django 1.2.x.

::

	$ pip install django-fiber


Requirements:
=============

These dependencies are automatically installed:

::

	PIL>=1.1.7
	djangorestframework==0.3.3
	django-compressor>=0.7.1

You need to install one dependency by hand when you're using Django 1.2.x:

::

	django-staticfiles>=1.0.1


Settings:
=========

settings.py
-----------

::

	import django.conf.global_settings as DEFAULT_SETTINGS

	MIDDLEWARE_CLASSES = DEFAULT_SETTINGS.MIDDLEWARE_CLASSES + (
	    'fiber.middleware.ObfuscateEmailAddressMiddleware',
	    'fiber.middleware.AdminPageMiddleware',
	    'fiber.middleware.PageFallbackMiddleware',
	)

	TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + (
	    'django.core.context_processors.request',
	    'staticfiles.context_processors.static_url',
	    'fiber.context_processors.page_info',
	)

	INSTALLED_APPS = (
	    ...
	    'staticfiles',
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
	STATICFILES_FINDERS = (
	    'staticfiles.finders.FileSystemFinder',
	    'staticfiles.finders.AppDirectoriesFinder',
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
	    urlpatterns += patterns('staticfiles.views',
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
