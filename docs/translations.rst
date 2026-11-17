Translations and Transifex
==========================

Transifex integration is temporarily disabled while its account setup is
unresolved. Its mappings in ``transifex.yml`` are commented out for future use.
Account setup and first-sync verification are deferred and do not block releases
or the next modernization branch.

Existing translations remain in Git. Submit translation changes through ordinary
pull requests and use the local validation and compilation steps below. Both
``django.po`` (Python/templates) and ``djangojs.po`` (JavaScript) remain supported,
with English source catalogues under ``fiber/locale/en/LC_MESSAGES/``.

If the native GitHub integration was already connected in Transifex, disable or
disconnect it in the Transifex dashboard too. Commenting out repository mappings
does not change account-side settings. No account-side change was made here.

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
any regenerated compiled files. Maintain source and translated catalogues in
Git while synchronization is disabled.

Review translation updates
--------------------------

Check out the translation pull request branch and run this from the repository
root::

    python bin/compile_translations.py

The command requires GNU gettext's ``msgfmt``. It validates syntax and marked
format placeholders and compiles both domains. Each existing ``.mo`` is replaced
only after its own compilation succeeds. If another catalogue fails, earlier
successful files may already have been updated; review the complete diff.

Commit the regenerated tracked ``.mo`` files with the reviewed ``.po`` changes
before merging. Repeat compilation when the PR changes. CI checks
that compilation leaves the committed catalogues unchanged. Empty and fuzzy
translations fall back to source strings; partial translations are welcome.

The prerelease hook performs the same local compilation. Releases use reviewed
translations already merged into Git. They neither download translations nor
wait for pending PRs, complete languages, or Transifex availability.

Future reactivation
-------------------

The following settings are retained for future use, not current setup work.
Before enabling synchronization, verify the existing resources and translations,
then uncomment ``transifex.yml`` and review the service settings below.

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

Recovery after reactivation
---------------------------

Once the integration is deliberately re-enabled, if updates stop arriving, inspect the integration activity log, linked branch,
configuration path, resource mapping, language codes, and GitHub app access.
An administrator can retry a sync independently of a release. Keep failed or
unexpected translation changes in an unmerged PR until reviewed and compiled.
Record the first successful sync and PR checks in the implementation record;
checked-in configuration alone does not establish that the service is connected.
