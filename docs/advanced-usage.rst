==============
Advanced usage
==============


This document is used to gather more advanced usage examples.


Optional settings
=================

These settings are optional (default values are shown):

::

    FIBER_LOGIN_STRING = '@fiber'

    FIBER_DEFAULT_TEMPLATE = 'base.html'
    FIBER_TEMPLATE_CHOICES = []
    FIBER_CONTENT_TEMPLATE_CHOICES = []

    FIBER_EXCLUDE_URLS = []

    FIBER_IMAGES_DIR = 'uploads/images'
    FIBER_FILES_DIR = 'uploads/files'

    FIBER_EDITOR = 'fiber.editor_definitions.ckeditor.EDITOR'

    FIBER_PAGE_MANAGER = 'fiber.managers.PageManager'
    FIBER_CONTENT_ITEM_MANAGER = 'fiber.managers.ContentItemManager'

    FIBER_METADATA_PAGE_SCHEMA = {}
    FIBER_METADATA_CONTENT_SCHEMA = {}

    FIBER_AUTO_CREATE_CONTENT_ITEMS = False

    COMPRESS = [the opposite of DEBUG]

    API_RENDER_HTML = False  # If set to True, you must include 'djangorestframework' in INSTALLED_APPS as well

    FIBER_IMAGE_PREVIEW = True  # If set to False, you don't need 'easy_thumbnails' in INSTALLED_APPS
    FIBER_LIST_THUMBNAIL_OPTIONS = {'size': (111, 111)}
    FIBER_DETAIL_THUMBNAIL_OPTIONS = {'size': (228, 228)}


Set or override fiber_page in a view
====================================

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


Set or override fiber_page in a class based view
================================================

In this example, the NewsItemDetailView's context is enriched with fiber_page and fiber_current_pages.

::

    from django.core.urlresolvers import reverse
    from django.views.generic import DetailView
    from fiber.views import FiberPageMixin


    class NewsItemDetailView(FiberPageMixin, DetailView):

        def get_fiber_page_url(self):
            return reverse('news_item_list')


Templates
=========

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


Metadata
========

In this example metadata (key-value pairs) for pages will be available in the backend-admin:

::

    FIBER_METADATA_PAGE_SCHEMA = {
        'title': {
            'widget': 'select',
            'values': ['option1', 'option2', 'option3',],
        },
        'bgcolor': {
            'widget': 'combobox',
            'values': ['#ffffff', '#fff000', '#ff00cc'],
            'prefill_from_db': True,
        },
        'description': {
            'widget': 'textarea',
        },
    }

The first key key is 'title'. Because it has widget 'select' you will have 3 fixed values to choose from.

The second key is 'bgcolor'. Because it has widget 'combobox' you will have 3 fixed values to choose from and the choice to add your own 'bgcolor'.
By setting prefill_from_db to True, the custom values you have chosen will also appear in the selectbox of fixed values.

The third key is 'description'. Because it has widget 'textarea' you can enter the value in a big textarea field.

Available widgets are:
    select
    combobox
    textarea
    textfield (default widget)

Only the combobox can prefill from the database by setting prefill_from_db = True (default=False)


The same metadata schema is available for metadata for content:

::

    FIBER_METADATA_CONTENT_SCHEMA



CKEditor config settings
========================

Some default CKEditor config settings can be altered by creating a file called admin-extra.js, which should be placed in a folder structure like this:

::

    appname/static/fiber/js/admin-extra.js

Make sure 'appname' is placed _before_ 'fiber' in settings.INSTALLED_APPS, otherwise the admin-extra.js file won't override the default admin-extra.js provided by Django Fiber.

The following config settings can be used in admin-extra.js to override default CKEditor behavior:

::

    window.CKEDITOR_CONFIG_FORMAT_TAGS = 'p;h1;h2;h3;h4';
    window.CKEDITOR_CONFIG_STYLES_SET = [
        { name: 'intro paragraph', element: 'p', attributes: { 'class': 'intro' } }
    ];
    window.CKEDITOR_CONFIG_EXTRA_PLUGINS = 'fpagelink,ffilelink,fimagelink,fcustomlink,funlink,fimage,table,tabletools';
    window.CKEDITOR_CONFIG_REMOVE_PLUGINS = 'scayt,language,menubutton,forms,image,link';
    window.CKEDITOR_CONFIG_ALLOWED_CONTENT = false;
    window.CKEDITOR_CONFIG_EXTRA_ALLOWED_CONTENT = 'a[*]{*}(*);img[*]{*}(*);iframe[*];object[*];param[*];embed[*]';
    window.CKEDITOR_TOOLBAR_CAN_COLLAPSE = false;
    window.CKEDITOR_CONFIG_MAX_WIDTH = 610;
    window.CKEDITOR_BASE_FLOAT_Z_INDEX = 1100;

You can also override the entire CKEditor toolbar, by setting the variable:

::

    window.CKEDITOR_CONFIG_TOOLBAR

To see how this works, check the fiber.ckeditor.js file in the Django Fiber source:
https://github.com/django-fiber/django-fiber/blob/master/fiber/static/fiber/js/fiber.ckeditor.js


.. _advanced_usage_custom_permissions:

Custom permissions
==================

Fiber provides a :mod:`fiber.permissions` module. The Permission class defined here can be overridden by writing a custom
permission class and pointing `PERMISSION_CLASS` in your settings module to that class.

Here's an example module that implements object level permissions:

.. literalinclude:: code-examples/permission_class.py

Sitemap
=======

.. automodule:: fiber.sitemaps
