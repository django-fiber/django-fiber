===========
Development
===========

New releases
============

In order to make releasing a new version slightly easier, this project has been set up to use
`Zest-releaser <http://zestreleaser.readthedocs.io/en/latest/>`_, which will need to be installed on your local dev
machine::

    pip install zest.releaser[recommended]

The `[recommended]` adds a number of optional packages that make Zest-releaser more convenient.

To use Zest.releaser: rather than copy-and-paste the excellent instructions from their docs,
`here is a link to their documentation <http://zestreleaser.readthedocs.io/en/latest/overview.html#available-commands>`_.

Note that the ``prerelease`` command has some custom hooks in order to:

1. Run all the unit tests before a release.
2. There is no 2!

.. note::

    In order for Django-Fiber to be uploaded to PyPI, you will need write privileges.

Translations
============

Translation strings are managed through Transifex - `here's the Django-Fiber project page <https://www.transifex.com/django-fiber/django-fiber/dashboard/>`_.

The intention is to always have several Transifex maintainers (at present there are 2).

If you are listed as maintainer on Transifex, here's a checklist of common actions that you can perform:

Pull from Transifex
-------------------
Get translated strings from Transifex and add them to your local copy of the project - the following assumes that you
have already set up your connection to Transifex on your local computer::

    cd <fiber folder of project>
    tx pull -a --force
    django-admin.py compilemessages

Push to Transifex
-----------------
If any strings in the project have been modified, they need to be sent up to Transifex for translation::

    cd <fiber folder of project>
    django-admin.py makemessages --all
    tx push --source --translations

