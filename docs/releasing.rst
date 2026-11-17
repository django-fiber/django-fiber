Release documentation on Read the Docs
======================================

Read the Docs builds pushed release tags through its native GitHub integration,
independently of PyPI publication. Each tag has versioned documentation;
``stable`` follows the newest final release and existing ``latest`` links
redirect to it. Package preparation and publication are described in
:doc:`development`.

Repository configuration
------------------------

``.readthedocs.yaml`` installs the checked-out project with its ``docs`` extra
and treats Sphinx warnings as errors. Python 3.12 matches the isolated release
command and is the newest interpreter supported by the current Django 4.2
branch. Documentation initializes Django for API documentation, so it needs a
compatible interpreter even though package builds can use a newer one.
No database migration or developer database replacement is needed.

The prerelease hook runs this command before preparing release commits::

    python -m sphinx -E -W --keep-going -b html docs docs/_build/html

The isolated release environment includes ``dev``, ``docs``, and ``release``
extras. A failed documentation build stops preparation. Locally, install
``python -m pip install -e '.[docs]'`` and use the same build command. Open
``docs/_build/html/index.html`` to inspect the result.

Read the Docs installs the tagged checkout; it does not download django-fiber
from PyPI. The package does not have to be published before its documentation
builds. No Read the Docs API token or custom publishing job is needed in
GitHub Actions.

One-time service setup
----------------------

An administrator must configure the existing django-fiber Read the Docs project:

1. Connect the django-fiber/django-fiber repository using the native GitHub
   integration and verify incoming events. Select ``.readthedocs.yaml`` as the
   configuration file.
2. Add an enabled automation rule with version type **Tag**, match **Any
   version**, and action **Activate version**. Add a second enabled rule with
   the same conditions and action **Trigger build for version**, with no file
   or commit-message filters. Fiber has two-component release tags such as
   ``1.11``; the SemVer match would miss these tags.
3. Disable automatic pull-request builds and other rules that activate or build
   branches or pull requests. Keep the tag build rule enabled: unmatched branch
   and pull-request events then do not trigger documentation builds.
4. After verifying a successful final-release build, keep ``stable`` active and
   select it as the default version. Read the Docs maintains this alias for the
   newest final release; prerelease tags must not move it.
5. Add a forced **Exact redirect** from ``/en/latest/*`` to
   ``/en/stable/:splat``. Check a deep link such as
   ``/en/latest/development.html`` as well as the documentation root. Once the
   redirect is verified, deactivate automatic branch versions, including
   ``latest``, while preserving the release versions.

These are account-side settings. The configuration file controls how a version
builds, not which repository events cause builds. Rules apply to new versions;
activate an existing version manually when needed. See the official
`automation rules <https://docs.readthedocs.com/platform/stable/automation-rules.html>`_
and `redirects <https://docs.readthedocs.com/platform/stable/user-defined-redirects.html>`_
references.

Verify the first build and the next release
-------------------------------------------

After pushing this implementation, manually build its exact commit using the
Read the Docs dashboard and verify the build's commit ID and log. If it is on
a review branch, temporarily activate that version for this manual build;
after acceptance, leave automatic branch and PR builds disabled. Inspect the
HTML output and follow navigation and API links. This check needs no package
upload or release tag.

At the next permitted final release, verify that its pushed tag triggers a
build and that its versioned documentation, ``stable``, and the ``latest``
redirect all serve the expected release. Until then, ``stable`` may continue
to serve the existing published version. Django 4.2 after branch 6b and Django
5.0 after branch 7 are permitted release milestones once their acceptance checks
pass. Create release tags only for accepted releases, rather than to test this
setup. Historical tag rebuilds are outside this work.

Record the tested commit, Python/Django/Sphinx versions, local build and warning
regression results, Read the Docs build URL and result, and alias/redirect checks
in the implementation PR. Identify any account-side setup still pending;
committed configuration alone does not prove the live integration works.

Publication recovery
--------------------

Before declaring a release complete or preparing the next release tag, check
both the GitHub Actions PyPI result and the Read the Docs release build.
Neither guarantees the other succeeded. A documentation failure does not roll
back PyPI publication, and must not trigger a repeated successful package upload.

For a failed documentation build, inspect its Read the Docs log. Correct account
settings or transient problems and retry the same version there. If no build
appeared, check integration events, automation rules, and version activation.
If source or configuration inside a published tag needs correction, prepare a
new release rather than moving that tag. Recheck the versioned documentation,
``stable`` alias, and deep-link redirect after recovery.
