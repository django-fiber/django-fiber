Translations and Transifex
==========================

Fiber's native Transifex GitHub integration maps two resources in
``transifex.yml``: ``django.po`` for Python/templates and ``djangojs.po`` for
JavaScript. The English source catalogues live under
``fiber/locale/en/LC_MESSAGES/``. Keep source strings in Git and translated text
in Transifex. The existing resources and their translation history must be
preserved when connecting the integration.

Source string changes
---------------------

Install the project and GNU gettext. On Ubuntu, install gettext with
``sudo apt install gettext``. From the repository root, extract both domains::

    cd fiber
    python -m django makemessages -l en -d django
    python -m django makemessages -l en -d djangojs
    cd ..
    python bin/compile_translations.py

Review and commit the English catalogue changes with the code change, including
any regenerated compiled files. Transifex reads the source catalogues after the
change reaches ``master``; the integration does not extract strings from code.
Do not replace the English catalogues with translations downloaded from Transifex.

Review translation updates
--------------------------

The integration sends batches of translations as pull requests. Check out the
PR branch and run this from the repository root::

    python bin/compile_translations.py

The command requires GNU gettext's ``msgfmt``. It validates syntax and marked
format placeholders and compiles both domains. Each existing ``.mo`` is replaced
only after its own compilation succeeds. If another catalogue fails, earlier
successful files may already have been updated; review the complete diff.

Commit the regenerated tracked ``.mo`` files with the reviewed ``.po`` changes
before merging. Repeat compilation if Transifex updates the PR again. CI checks
that compilation leaves the committed catalogues unchanged. Empty and fuzzy
translations fall back to source strings; partial translations are welcome.

The prerelease hook performs the same local compilation. Releases use reviewed
translations already merged into Git. They neither download translations nor
wait for pending PRs, complete languages, or Transifex availability.

Integration settings
--------------------

In the existing Transifex project's Settings > Integrations > GitHub:

* Restrict the GitHub app to ``django-fiber/django-fiber``.
* Link ``master`` and select ``transifex.yml``. Test the configuration and verify
  both source paths, English source language, and detected translation paths.
* Link the existing core and JavaScript resources before the first sync.
  Confirm their identity and history rather than accepting duplicate resources.
  Follow the official `existing-resource migration procedure
  <https://help.transifex.com/en/articles/8065148-github-auto-syncing-and-management>`_.
* Select translated content with the lowest permitted custom threshold.
* Use **Create a Pull Request**, grouped by **All resources and languages**,
  with a **60-minute** interval between commits.
* Disable **Receive updates for source files**; source changes belong in Git.

These are account-side settings. The YAML file specifies mappings, not account
permissions or batching policy. No custom GitHub synchronization workflow or
release-time Transifex credential is needed. The old ``.tx/config`` CLI setup
is retired. See the official `installation and configuration guide
<https://help.transifex.com/en/articles/6265125-github-installation-and-configuration>`_.

Before saving the first integration, verify the existing resources and detected
language codes in the account. Retain both English source files even though
their translations are empty. The existing ``no`` catalogues also contain no
translated messages and remain in Git for fallback compatibility. If the service
rejects empty target catalogues, resolve that with the administrator before
syncing; do not delete nonempty translations or existing resources to bypass an
import error. Review and compile the first translation PR before merging it.

Maintenance and recovery
------------------------

If updates stop arriving, inspect the integration activity log, linked branch,
configuration path, resource mapping, language codes, and GitHub app access.
An administrator can retry a sync independently of a release. Keep failed or
unexpected translation changes in an unmerged PR until reviewed and compiled.
Record the first successful sync and PR checks in the implementation record;
checked-in configuration alone does not establish that the service is connected.
