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

Before preparing a release, the hook runs release-tool tests, ``./run_tests``,
migration and Django system checks, Python compilation checks, manifest
validation, and a clean distribution build with strict metadata validation.
There is no new project-wide lint policy. A failing check stops preparation.

Zest prepares local release commits and a tag, then advances the development
version. Automatic pushes, distribution uploads, and Zest's distribution
checkout/build step are disabled. Do not publish from a transitional branch;
see the release gates in ``docs/upgrade-plan.md``.

Distribution build workflow
---------------------------

The manually dispatched ``publish-pypi.yml`` workflow must run from ``master``.
It checks that the tag matches the source version, is checked out exactly, and
is contained in ``master``. It builds on Python 3.14 without installing Django
or application dependencies; application tests remain on their planned matrix.
The wheel and source metadata must both identify django-fiber at the tagged
version, and strict Twine validation must pass.

Artifacts are named with the run ID and build attempt and retained for 30 days.
A rebuild gets a new artifact. A later publication retry must use the original
successful build's artifact ID, rather than deriving a name from its own attempt.
There are no TestPyPI builds or uploads.

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
