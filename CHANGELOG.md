# Changelog

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
* Django 1.5 compatiblity fixes
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
