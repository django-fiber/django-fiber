# Changelog

## 0.11.0

**Date**: 9th Oct 2013

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

## 0.10.5

**Date**: 27th Aug 2013

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

[issue180]: https://github.com/ridethepony/django-fiber/issues/180
[issue175]: https://github.com/ridethepony/django-fiber/pull/175

## 0.10.4

**Date**: 3rd Jul 2013

* Upgraded Django REST Framework to 2.3.6

## 0.10.3

**Date**: 25th Apr 2013

* Upgraded external packages to the latest stable releases:
    * Django REST Framework 2.2.6
    * Django Compressor 1.3
    * Pillow 2.0.0
* Extended the Permission Class with a method that allows a developer to control if
  a user can see the Fiber admin interface
* Bugfixes:
    * Fixed a [bug][issue171] in the middleware which was introduced in 0.10.2 if using Django 1.3
    * Thanks to the upgrade of Django REST Framework [this issue][issue] is also resolved.

[issue171]: https://github.com/ridethepony/django-fiber/pull/171
[issue]: https://github.com/tomchristie/django-rest-framework/issues/705


## 0.10.2

**Date**: 22nd Mar 2013

* Django 1.5 compatibility fixes
* block non-POST requests on login
* updated external libraries
    * Fine Uploader 3.2.0
    * CKEDITOR 4.0.1
* improved testing
    * test multiple Django and Python versions on Travis CI
    * added tox support


## 0.10.1

**Date**: 7th Feb 2013

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


## 0.10

**Date**: 21st Dec 2012

* Enhancement: Ported to REST Framework. **Note:** projects with local REST Framework 0.3.X or 0.3.4
dependencies will break.
* Enhancements: Updated README file and added this changelog.


## 0.9.9.1

**Date**: 6th Dec 2012

* Security-Bugfix: Changed permission check in API from IsAuthenticated to IsAdminUser


## 0.9.9

**Date**: 27th Nov 2012

* Enhancement: Title fields of pages are now required. Solves inconsistent behaviour in the UI.

---

Older changes not documented. Revert to the git log for details.
