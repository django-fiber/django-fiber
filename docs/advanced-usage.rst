==============
Advanced usage
==============


This document is used to gather more advanced usage examples.


Optional settings:
==================

These settings are optional (default values are shown):

::

	FIBER_DEFAULT_TEMPLATE = 'base.html'
	FIBER_TEMPLATE_CHOICES = []
	FIBER_CONTENT_TEMPLATE_CHOICES = []

	FIBER_EXCLUDE_URLS = []

	FIBER_IMAGES_DIR = 'uploads/images'
	FIBER_FILES_DIR = 'uploads/files'

	FIBER_METADATA_PAGE_SCHEMA = {}
	FIBER_METADATA_CONTENT_SCHEMA = {}

	COMPRESS = [the opposite of DEBUG]


Set or override fiber_page in the view:
=======================================

In this example, the news_item_detail view looks up the Page of the news_item_list by looking up its named URL. This way, you can reuse the content you have placed on the news_item_list Page for each news_item_detail Page.

::

	def news_item_detail(request, news_item_slug):
	    news_item = get_object_or_404(NewsItem, slug=news_item_slug)

	    fiber_page = Page.objects.get(url__exact='"news_item_list"')

	    t = loader.get_template('news_item_detail.html')
	    c = RequestContext(request, {
	        'fiber_page': fiber_page,
	        'news_item': news_item
	    })
	    return HttpResponse(t.render(c))


Templates:
==========

In this example 4 page-templates will be available in the front- and backend-admin:

::

	FIBER_TEMPLATE_CHOICES = (
		('', 'Default template'),
		('tpl-home.html', 'Home template'),
		('tpl-intro.html', 'Intro template'),
		('tpl-with-sidebar.html', 'With sidebar template'),
	)

The first choice '' will load the FIBER_DEFAULT_TEMPLATE, default this is 'base.html'


In this example 2 content-templates will be available in the front- and backend-admin:

::

	FIBER_CONTENT_TEMPLATE_CHOICES = (
		('', 'Default template'),
		('special-content-template.html', 'Special template'),
	)

The first choice '' will load the default content-template, this is 'fiber/content_item.html'


CKEditor config settings
========================

Some default CKEditor config settings can be altered by creating a file called admin-extra.js, which should be placed in a folder structure like this:

::

	appname/static/fiber/js/admin-extra.js

Make sure 'appname' is placed _before_ 'fiber' in settings.INSTALLED_APPS, otherwise the admin-extra.js file won't override the default admin-extra.js provided by Django Fiber.

Something like this should be placed in admin-extra.js:

::

	window.CKEDITOR_CONFIG_FORMAT_TAGS = 'p;h1;h2;h3;h4';
	window.CKEDITOR_CONFIG_STYLES_SET = [
		{ name: 'intro paragraph', element: 'p', attributes: { 'class': 'intro' } }
	];

You can also override the entire CKEditor toolbar, by setting the variable:

::

	window.CKEDITOR_CONFIG_TOOLBAR

To see how this works, check the fiber.ckeditor.js file in the Django Fiber source:
https://github.com/ridethepony/django-fiber/blob/master/fiber/static/fiber/js/fiber.ckeditor.js