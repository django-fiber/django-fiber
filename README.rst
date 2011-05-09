=====
Fiber
=====

Installation:
=============

::

	$ pip install django-fiber


Requirements:
=============

These dependencies are automatically installed:

::

	django-mptt>=0.4.2
	django-piston==0.2.3rc1
	django-staticfiles>=1.0.1
	beautifulsoup>=3.2.0
	django-compressor>=0.7.1

Optionally, you may need:

::

	textile>=2.1.5
	South>=0.7.3


Settings:
=========

settings.py
-----------

::

	MIDDLEWARE_CLASSES = (
		...
		'fiber.middleware.ObfuscateEmailAddressMiddleware',
		'fiber.middleware.AdminPageMiddleware',
		'fiber.middleware.PageFallbackMiddleware',
		...
	)

	TEMPLATE_CONTEXT_PROCESSORS = (
		...
		'django.core.context_processors.request',
		'staticfiles.context_processors.static_url',
		'fiber.context_processors.page_info',
		...
	)

	INSTALLED_APPS = (
		...
		'mptt',
		'staticfiles',
		'compressor',
		'fiber',
		...
	)

	import os
	STATIC_ROOT = os.path.join(MEDIA_ROOT, 'static')
	STATIC_URL = MEDIA_URL + 'static/'
	STATICFILES_MEDIA_DIRNAMES = (
		'static',
	)
	STATICFILES_FINDERS = (
		'staticfiles.finders.FileSystemFinder',
		'staticfiles.finders.AppDirectoriesFinder',
		'compressor.finders.CompressorFinder',
	)

	COMPRESS_JS_FILTERS = ()


Optional settings:
==================

These settings are optional (default values are shown)::

	FIBER_DEFAULT_TEMPLATE = 'base.html'
	FIBER_TEMPLATE_CHOICES = []

	FIBER_EXCLUDE_URLS = (r'^admin/',)

	FIBER_IMAGES_DIR = 'uploads/images'
	FIBER_FILES_DIR = 'uploads/files'

	COMPRESS = [the opposite of DEBUG]


urls.py
-------

::

	...
	(r'^api/v1/', include('fiber.api.urls')),
	(r'^admin/fiber/', include('fiber.admin_urls')),
	(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {'packages': ('fiber',),}),
	...


Post-installation:
==================

Create database tables::

	$ python manage.py syncdb

All static Fiber files need to be symlinked in (or copied to) your media folder::

	$ python manage.py collectstatic --link


Usage:
======

At the beginning of your template(s), load the Fiber template tags::

	{% load fiber_tags %}

Using the Fiber template tags, you can:

- write out content items, that either

  - have a specified name
  - are linked to a specific location on the current page
  - are linked to a specific location on another page

- write out valid XHTML menu structures

  - of pages below a named root page (this is the menu name),
  - limited to a minimum and maximum level (depth),
  - that mark the currently active page,
  - optionally expanding all descendants of the currently active page,
  - with all possible css hooks you could ever need


Content items
-------------

You can write out content items with the 'show_content' and 'show_page_content' template tags::

	{% show_content "content_item_name" %}
	{% show_page_content "block_name" %}
	{% show_page_content other_page "block_name" %}

Examples
........

This shows content item named 'address'::

	{% show_content "address" %}

This shows content items that are linked to the location named 'content' on the current page::

	{% show_page_content "content" %}

This shows content items that are linked to the location named 'content' on another page 'other_page'::

	{% show_page_content other_page "content" %}


Menus
-----

You can write out menus with the 'show_menu' template tag::

	{% show_menu "menu_name" min_level max_level ["all_descendants / all"] %}

The menu name refers to a top-level node in the page tree.

Examples
........

The examples below assume the pages are structured like this:

- mainmenu

  - Home
  - About us

    - Mission
    - Our people

  - Products

    - Product A

      - Testimonials
      - Downloads

        - Technical data sheet
        - User manual

    - Product B

      - Downloads

    - Product C

      - Downloads

  - Contact

    - Newsletter
    - Directions

- generalmenu

  - Disclaimer
  - Privacy statement

Main menu
.........

Show first and second level pages, below the root page named 'mainmenu'::

	{% show_menu "mainmenu" 1 2 %}

When the user is currently visiting the 'Home' page, this will show (current pages are bold):

- **Home**
- About us
- Products
- Contact

When the user is currently visiting the 'Products' page, this will show:

- Home
- About us
- **Products**

  - Product A
  - Product B
  - Product C

- Contact

As you can see, the sub pages of the currently active 'Products' page are automatically expanded.

When the user is currently visiting the 'Product A' page, this will show:

- Home
- About us
- **Products**

  - **Product A**
  - Product B
  - Product C

- Contact

The sub pages of the 'Product A' page are not shown, because they are outside of the specified minimum and maximum levels.

Sub menu
........

Show pages from level 3 to 5, below the root page named 'mainmenu', and also show all descendants of the currently active page::

	{% show_menu "mainmenu" 3 5 "all_descendants" %}

When the user is currently visiting the 'Home' page, this will show an empty menu, since it cannot be determined what level 3 pages are currently active.

However, when the user is currently visiting the 'Product A' page, this will show:

- **Product A**

  - Testimonials
  - Downloads

    - Technical data sheet
    - User manual

- Product B
- Product C

Notice that all pages below the currently active 'Product A' page are expanded because of the 'all_descendants' parameter.

Sitemap
.......

Show all pages, with all pages expanded::

	{% show_menu "mainmenu" 1 999 "all" %}
	{% show_menu "generalmenu" 1 999 "all" %}
