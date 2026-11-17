===========
Development
===========

New releases
============

Prepare releases from a clean checkout of ``master`` with an isolated environment::

    uvx --python 3.12 --from zest.releaser --with-editable '.[dev,release]' fullrelease

Python 3.12 is the newest interpreter supported by this branch's Django 4.2.
Use its latest patch. This tooling choice does not change the Python 3.10
application baseline. The command installs the project and release tools in
its own environment; it does not use the active virtual environment.

Zest prepares local release commits and a tag, then advances the development
version. Automatic pushes, distribution uploads, and Zest's distribution
checkout/build step are disabled. Do not publish from a transitional branch;
see the release gates in ``docs/upgrade-plan.md``.

Development and documentation dependencies
==========================================

Install development tools from the repository root::

    python -m pip install -e '.[dev]'

Run the tests with ``./run_tests`` or the compatibility matrix with ``tox``.

Install documentation tools and build HTML from the repository root::

    python -m pip install -e '.[docs]'
    python -m sphinx -W -b html docs docs/_build/html

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
