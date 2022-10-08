Changelog for Django-Fiber
==========================

1.10 (2022-10-08)
-----------------

- Checked compatibility with Django 4.0, 4.1.


1.9.1 (2021-11-02)
------------------

-  X-frame-options change broke the page editor - see #289.


1.9 (2021-10-22)
----------------

- Django 3.2 support.


1.8.1 (2020-09-15)
------------------

- Add missing .py extension to newly added migration. Really fixes #278


1.8 (2020-08-27)
----------------

- Django 3.1 support
- New migration (required because the Page model is based on django-mptt, and django-mptt has removed a number of
  indexes from fields - django-fiber itself has not changed). See #278

1.7 (2020-05-09)
----------------

- Django 3.0 support.
- Python 3.8 support
- Dropped Django 1.11, 2.0, 2.1.
- Dropped Python 2.7.
- Reset 'Content-Length' header in AdminPageMiddleware and
  ObfuscateEmailAddressMiddleware to make sure clients read
  the full response.

1.6.1 (2019-10-17)
------------------

- Specified more precisely django-mptt version.


1.6 (2019-06-20)
----------------

- Django 2.1 and 2.2 support.
- Fix for #261: Fiber admin crashes if non-Fiber models use non-integer primary keys.
- dumpdata fiber was broken (#262).
- fixed an issue with content item cache (#263).
- Removed a Fiber context processor that had been deprecated for several years.
- Removed code for South migrations.

1.5 (2018-01-19)
----------------

* Django 2.0 support
* Python 3.6 support
* Dropped Django 1.8 support as A/ django-rest-framework no longer supports it B/ it will be end-of-lifed
  in a few months anyway.
* Updated translations strings (Spanish, Norwegian, Portuguese).
* Updated docs.

1.4.1 (2017-09-12)
------------------

* Django 1.11 support
* Python 3.5 support
* Support new style middleware
* Fix issues with migrations
  * Django used to create a migration when the file/image upload directory setting changed
  * Django used to create a migration for the default manager

1.4.0 (2017-01-23)
------------------

* Upgraded CKEditor 4.5.4 -> 4.6.2
* Updates and improvements of README
* Updated test project
* Correction in migrations: on_delete will be required for ForeignKeys in the future
* Fix API to work with django-rest-framework >= 3.4
* Updated dependencies to versions that support Django >= 1.8
* Added Django 1.9 and 1.10 support
* Added Python 3.4 support
* Dropped Django < 1.8 support
* Dropped Python < 2.7 support


1.3.1 (2015-10-27)
------------------

* upgrade CKEditor 4.4.7 -> 4.5.4


1.3 (2015-10-27)
------------------

* run tests on Django 1.8, fix test failure
* tox.ini uses new features of tox
* load Fiber page data and contentitem groups async, makes navigating pages with Fiber enabled much faster
* fix incompatibility with django-compressor running in offline mode
* handle lazy URLs
* fix behaviour of show_page_content for non-Fiber pages
* make editable_attrs a bit smarter
* use a box shadow to show editable items
* don't open a dialog window for unknown editable items, go to the edit url instead, in a new tab / window
* enable context menu to edit non-Fiber items
* fix context menu for non-page contentitems
* open the correct dialog (content item vs page) on double click
* refactor and test show_menu and other template tags, use generator expressions
* refactor deprecated page_info contextprocessor to reuse FiberPageMixin logic
* fixed an issue where the root node was included when mark_current_regexes matches
* test and refactor FiberPageMixin, FiberTemplateView
* test and refactor AdminPageMiddleware, ObfuscateEmailAddressMiddleware
* refactor import_util, load_class
* overall test and test coverage improvements
* numerous small fixes and improvements


1.2 (2015-07-29)
------------------

* Implemented Django's static template tag to support Django 1.8
* Fixed an error where context menu would not show when right-clicking a fiber content item


1.1 (2015-02-10)
------------------

* Updated Sphinx settings to work with Django 1.7
* Upgraded CKEditor 4.3.2 -> 4.4.7
* Re-use of default CKEditor icons for most of the icons
* CKEditor icons now also support hidpi/retina screens
* Corrections for aggressive styling in dialogs
* Brought back the original South migrations in there own `south_migrations` directory
* Fixed login issue with Django 1.7
* Pinned djangorestframework to >=2.3.8,<3.0 in setup.py
* Fixed image selectors in markitup editor
* Fixed easy_thumbnails exceptions
* Handle ProtectedErrors user friendly
* Fine-tunes in several (new) messages and their Dutch translations


1.0 (2014-11-26)
------------------

* Support Django 1.7


0.13 (2014-04-01)
------------------

* More config settings for CKEditor (this is no joke)


0.12.2 (2014-02-18)
------------------

* Fixed object style selection in new CKEditor
* Allow classes and styles on a and img elements


0.12.1 (2014-02-13)
------------------

* Quick fix - don’t let the new CKEditor strip out a and img tags


0.12 (2014-02-13)
------------------

* (re)allow embedding of media using iframes, objects (with params and embed)
* Fixed 500 error that occurred when adding a Fiber Image without providing a title
* Return an informative text instead of raising 500 errors when image files are missing


0.11.4 (2014-02-11)
------------------

* Fixed issue with non-workinbg CKEditor when no stylesSet is defined


0.11.3 (2014-02-11)
------------------

* Upgraded CKEditor to 4.3.2
* Correctly reverse admin urls instead of relying on relative paths


0.11.2 (2014-01-29)
------------------

* Added fix for issue with protected ForeignKey relations
* Added sitemap.xml support
* Added missing image and fixed image paths


0.11.1 (2013-10-14)
------------------

* New feature: Auto add content items, pull request [pull182]

    When you use the fiber tag {% show_content "content_name" %} the content item will be automatically created if it not already exists.

        # settings.py
        FIBER_AUTO_CREATE_CONTENT_ITEMS = True

        # template.html
        {% show_content "content_name" %}

* Added [coveralls.io] support, pull request [pull176]

[pull182]: https://github.com/django-fiber/django-fiber/pull/182
[pull176]: https://github.com/django-fiber/django-fiber/pull/176
[coveralls.io]: https://coveralls.io/r/django-fiber/django-fiber


0.11.0 (2013-10-09)
------------------

* Image previews for Fiber Image in the Django admin
    * Using Easy Thumbnails 1.4
    * Optional with new setting `FIBER_IMAGE_PREVIEW`
    * Configurable thumbnail_options for both change_list and change_form
    * The thumbnail in the front-end imageselect pop-up also profits from easy_thumbnails when installed
* Dropped support for Django 1.3.x
* Upgraded external packages to the latest stable releases:
    * Pillow to 2.2.1
    * Django REST Framework to 2.3.8
* Fixed a bug when change_list for Fiber Image was rendered in a popup, for instance called from a raw_id widget


0.10.5 (2013-08-27)
------------------

* Added meta_keywords field to Fiber Page model, so now you can add metatag keywords to your template. Ex:

        {% if fiber_page.meta_keywords %}
            <meta charset="utf-8" name="keywords" content="{{ fiber_page.meta_keywords }}" />
        {% endif %}

* Added doc_title field to Fiber Page model, useful for adding a custom document title to your template. Ex:

        <title>
            {% if fiber_page.doc_title %}
                {{ fiber_page.doc_title }}
            {% else %}
                {{ fiber_page.title }}
            {% endif %}
        </title>

* Prefix css classes in fiber frontend sidebar
    * See [issue180]
* Show a boolean True/False icon in the Django admin if a ContentItem is not used.
    * See [issue175]
* Upgraded external packages to the latest stable releases:
    * Pillow to 2.1.0
    * Django MPTT to 0.6
    * Django REST Framework to 2.3.7

[issue180]: https://github.com/django-fiber/django-fiber/issues/180
[issue175]: https://github.com/django-fiber/django-fiber/pull/175


0.10.4 (2013-07-03)
------------------

* Upgraded Django REST Framework to 2.3.6


0.10.3 (2013-04-25)
------------------

* Upgraded external packages to the latest stable releases:
    * Django REST Framework 2.2.6
    * Django Compressor 1.3
    * Pillow 2.0.0
* Extended the Permission Class with a method that allows a developer to control if
  a user can see the Fiber admin interface
* Bugfixes:
    * Fixed a [bug][issue171] in the middleware which was introduced in 0.10.2 if using Django 1.3
    * Thanks to the upgrade of Django REST Framework [this issue][issue] is also resolved.

[issue171]: https://github.com/django-fiber/django-fiber/pull/171
[issue]: https://github.com/tomchristie/django-rest-framework/issues/705


0.10.2 (2013-05-22)
------------------

* Django 1.5 compatibility fixes
* block non-POST requests on login
* updated external libraries
    * Fine Uploader 3.2.0
    * CKEDITOR 4.0.1
* improved testing
    * test multiple Django and Python versions on Travis CI
    * added tox support


0.10.1 (2013-02-07)
------------------

* updated Django REST Framework to 2.1.17
* updated requirements
    * Pillow 1.7.8
    * Django MPTT 0.5.5
    * Django compressor 1.2
    * Django REST Framework 2.1.17
* Django 1.5 compatibility fixes
* added meta_description field to Page
* added has_visible_children method to Page
* improved file deletion for multiple storage backends


0.10 (2012-12-21)
------------------

* Enhancement: Ported to REST Framework. **Note:** projects with local REST Framework 0.3.X or 0.3.4
dependencies will break.
* Enhancements: Updated README file and added this changelog.


0.9.9.1 (2012-12-06)
--------------------

* Security-Bugfix: Changed permission check in API from IsAuthenticated to IsAdminUser


0.9.9 (2012-11-27)
------------------

* Enhancement: Title fields of pages are now required. Solves inconsistent behaviour in the UI.

---

Older changes not documented. Refer to the git log for details.
