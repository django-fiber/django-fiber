===========
Development
===========

New releases
============

Prepare releases from a clean checkout of ``master`` with an isolated environment::

    uvx --python 3.12 --from zest.releaser --with-editable '.[dev,docs,release]' fullrelease

Python 3.12 is the newest interpreter supported by this branch's Django 4.2.
Use its latest patch. This tooling choice does not change the Python 3.10
application baseline. The command installs the project and release tools in
its own environment; it does not use the active virtual environment.

Before preparing a release, the hook runs release-tool tests, ``./run_tests``,
migration and Django system checks, Python compilation checks, strict Sphinx
documentation builds, manifest validation, and a clean distribution build with
strict metadata validation.
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

Trusted publishing setup and recovery
--------------------------------------

A maintainer must configure the existing django-fiber PyPI project with a
GitHub trusted publisher: owner ``django-fiber``, repository ``django-fiber``,
workflow ``publish-pypi.yml``, and environment ``pypi``. Create that GitHub
Actions environment with required reviewers, prevent self-review, and restrict
its deployment branch to ``master``. No PyPI API token is needed.

The repository variable ``PYPI_PUBLISH_ENABLED`` defaults to absent/disabled.
Set it to ``true`` only after the backend release gate (branch 13) and branches
6, 6a, and 6b have been accepted. Keep it disabled throughout transitional
implementation. The frontend milestone is branch 21. Environment reviewers
must verify the relevant acceptance record and tag before approving publication.
See the `trusted publisher documentation
<https://docs.pypi.org/trusted-publishers/adding-a-publisher/>`_.

A publish-only rerun downloads the artifact ID output by the successful build,
including when the rerun's attempt number has changed. For transient failures,
rerun only failed jobs, for example ``gh run rerun RUN_ID --failed``. Do not
restart a build after any file for that version has reached PyPI.

For a partial upload, the retry checks existing filenames and SHA256 hashes
against the retained artifact before skipping identical uploaded files. Changed
or unexpected files stop publication; never overwrite them or move the tag.
If the artifact has expired or its hashes disagree, stop and investigate; a
corrected source requires a new version. Check both wheel and source archive
on PyPI before marking publication complete. A successful upload needs no retry.

Prepare, push, publish, and verify
----------------------------------

Only prepare a real release after its acceptance gate. Start with a clean,
up-to-date ``master`` and reviewed changelog, then run the isolated command above.
Do not use ``--no-input`` on a developer checkout for verification: it makes real
release commits and tags. Validation of this tooling uses disposable repositories.

Zest leaves a release commit and tag followed by a development-version commit.
Push both commits and the release tag yourself. For example, replace ``TAG``
with the exact release tag::

    git push origin master
    git push origin refs/tags/TAG
    gh workflow run publish-pypi.yml --repo django-fiber/django-fiber --ref master -f release_tag=TAG

The postrelease hook normally runs before that push. It checks the release tag
on the commit preceding the development commit, compares the remote tag object
with the local tag, and checks GitHub CLI authentication before dispatching.
An unavailable tag, missing CLI, authentication error, or failed dispatch prints
a recoverable manual command and does not undo the completed local preparation.
After fixing the cause and pushing, run that command; do not repeat fullrelease.

Watch the workflow in GitHub Actions and check both distributions on PyPI.
A dispatched workflow, a successful local preparation, or a skipped publication
job is not a completed publication. Also verify the Read the Docs release build
and aliases as described in :doc:`releasing`. Transifex management follows in
branch 6b.

Development and documentation dependencies
==========================================

Install development tools from the repository root::

    python -m pip install -e '.[dev]'

Run the tests with ``./run_tests`` or the compatibility matrix with ``tox``.

Install documentation tools and build HTML from the repository root::

    python -m pip install -e '.[docs]'
    python -m sphinx -E -W --keep-going -b html docs docs/_build/html

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
