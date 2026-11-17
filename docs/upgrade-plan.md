# Incremental django-fiber modernization

## Purpose

This document is the canonical plan for modernizing django-fiber. The work is
split into a linear stack of branches. Branch 1 was created directly from
`master`; after branches 0 and 1 are merged, branch 2 is created from the
updated `master`, and each later branch is based on its predecessor. Every
branch must pass its automated and manual acceptance checks before work starts
on the next branch.

The initial compatibility target is Python 3.10 with Django 4.2. The final
backend target for this modernization pass is Python 3.11 through 3.14 with
Django 5.2 LTS. Python 3.10 is a transitional interpreter for the Django 4.2
through 5.2 upgrade and is removed before the first backend modernization
release. Frontend dependencies are upgraded conservatively, ending on jQuery
3.7.1 and the last open-source CKEditor 4 release rather than combining
dependency upgrades with complete UI rewrites.

This pass also covers release documentation on Read the Docs and translation
management through Transifex's native GitHub integration. Both services remain
independent of package publication; releases include reviewed translations
already merged into the repository.

## Working rules

- Each numbered section below corresponds to a distinct Git branch.
- Lettered branches are inserted follow-ups: branch 4 is already merged, so
  complete 4a before 6; complete 6, 6a, and 6b before starting 7. The former
  branch 5 is folded into branch 6 so publishing workflows and zest.releaser
  upgrades are reviewed together. Keep the later branch numbers and publication
  gates unchanged.
- `upgrade/01-repository-hygiene` is based directly on `master`, independently
  of the planning branch. Merge branches 0 and 1 before creating branch 2 from
  the updated `master`; base each later branch on its predecessor.
- Merge or approve each branch before creating its successor.
- Run the complete automated checks on every branch that changes executable
  code, dependencies, packaging, CI, or release behavior.
- Complete the manual browser checklist on every Django, Python, or JavaScript
  upgrade branch.
- Record test results, manual approval, blockers, and deviations in the
  corresponding pull request or tracking issue.
- When a branch establishes or changes the default local Python version, add or
  update the root `.python-version`. Keep the full supported-version matrix in
  tox and CI rather than using `.python-version` as a replacement for it.
- Use `uv` for optional interpreter/environment bootstrap and isolated release
  preparation. Keep the test wrapper, tox configuration, dependency files, and
  CI usable without requiring `uv`.
- Explicitly select and record the Python major/minor for build, release, and
  documentation tools, accepting its latest compatible patch. Prefer the newest
  stable, supported interpreter compatible with the dependencies each command
  actually loads. Commands that initialize Django must respect its Python
  compatibility table; build-only tools may use a newer interpreter. Verify
  tooling environments separately from the branch's application test matrix:
  this does not advance the planned public Python support or local baseline.
- Do not publish a modernization release from a transitional Django branch.
  The planned publication gates are the completed backend milestone at branch
  13 and the completed frontend milestone at branch 21.
- Update this document if implementation findings require the sequence or target
  to change.
- Do not commit `testproject/testproject_db`; it is local test-project data.

## Branch sequence

### 1. `upgrade/01-repository-hygiene`

- Base this branch directly on `master`, independently of the planning branch.
- Add root `.idea/` and `/testproject/testproject_db` entries to `.gitignore`.
- Remove the database from Git tracking without deleting or overwriting the
  developer's local file.
- Normalize ignores for build, coverage, tox, collected static, media, and local
  environment artifacts.

### 2. `upgrade/02-agent-guidance`

- Add an `AGENTS.md` adapted from django-minipub.
- Document the project layout, supported commands, correct test-project
  invocation, changelog rules, compatibility-upgrade runbook, pull-request
  expectations, and manual frontend checklist.
- Document optional local bootstrap with `uv python install` and
  `uv venv --managed-python`, while keeping the project commands tool-neutral.
- Require tests to run from the repository root through the supplied wrapper.
- Require migration checks with `makemigrations --check --dry-run`.

### 3. `upgrade/03-django42-python310`

- Port the useful changes from the existing `origin/django42` branch rather than
  recreating them.
- Target Django 4.2.30 on Python 3.10.
- Add a root `.python-version` specifying Python 3.10 so tools such as `uv` use
  the intended interpreter for local development and test setup.
- Set the minimum compatible versions to django-mptt 0.18, django-compressor
  4.6, Django REST framework 3.17.1, and easy-thumbnails 2.10.1.
- Add cross-platform Python scripts that run current, isolated
  `django-upgrade` and `pyupgrade` versions across all tracked Python files
  except migrations. Run them for Django 4.2 and Python 3.10 before manual
  compatibility work.
- Align dependency bounds, tox, CI, classifiers, README, and changelog.
- Resolve project-owned deprecation warnings, including the test import of
  `django.utils.timezone.utc` and the sitemap protocol warning.

The historical Django 4.2 branch was verified during planning: all 196 tests
passed on Python 3.10 with Django 4.2.30 and current compatible dependencies.

### 4. `upgrade/04-modern-packaging`

- Port the intent of django-minipub commit
  `8e1f16bc369a5d62e2b979c97f50cf5d1f3f81b4`.
- Move package metadata and runtime dependencies into `pyproject.toml`.
- Use `setuptools.build_meta` and set `requires-python` to `>=3.10`.
- Remove the obsolete `setup.py` publishing shim and universal-wheel
  configuration.
- Separate runtime, test/development, documentation, and release requirements.
- Add current project URLs, classifiers, package discovery, dynamic version
  lookup, license metadata, and build-artifact ignores.
- Validate wheel and source distribution contents with `python -m build`,
  `twine check --strict`, and `check-manifest`.

### 4a. `upgrade/04a-dependency-consolidation`

- Follow up the merged packaging branch using django-minipub commit
  `fe22faa54357838596108512d7ff5188a00c6aa9` as an example.
- Make `pyproject.toml` the authoritative runtime dependency list. Remove
  duplicated declarations and redundant requirements files. Update installation
  commands to install the project and its named extras directly, rather than
  retaining requirements files that only reference the project or an extra.
- Keep development, documentation, and release dependencies separated by role,
  using extras or tooling requirements without copying runtime bounds.
- Update tox, CI, Read the Docs installation, manifests, README, and contributor
  instructions together. Verify clean installations through each documented
  path and rerun package validation and the full application suite.

### 6. `upgrade/06-isolated-release-automation`

This branch combines the former publishing-workflow step with the zest.releaser
upgrades. Implement and validate publication without uploading to PyPI. Actual
publication waits for branches 6, 6a, and 6b to be complete and the applicable
backend or frontend release gate to be accepted.

- Port the intent of django-minipub commit
  `d02ca2c05513eb1985387c48eb03f793daeab6b4`.
- Add a manually dispatched production PyPI workflow only. Do not add TestPyPI
  builds, development-version rewriting, or TestPyPI publisher configuration.
- Build once, validate the version and tag, retain immutable artifacts, and
  publish through GitHub trusted publishing with least-privilege permissions.
- Require the workflow itself to run from `master` and the release tag to be
  contained in `master`. Validate tag, source version, and built distribution
  metadata before publication.
- Use attempt-specific artifact names when rebuilding. Retrying only a failed
  publish job must reuse the original validated artifacts. Document recovery
  from partial uploads without rebuilding or replacing published files.
- Select a build interpreter using the tooling rule above rather than copying
  django-minipub's Python 3.14 setting without validation.
- Document the external GitHub environment and PyPI trusted-publisher setup.
  Validate builds and failure/retry paths without uploading; the first real
  PyPI publication still requires the branch 13 or 21 acceptance gate.

- Port the intent of django-minipub commit
  `c772f3ed158532419ad99ef1607437d9b9a11c6a`.
- Move release hooks into a dedicated `release` package.
- Run zest.releaser in an isolated `uvx` environment.
- Pass `--python` explicitly: `uvx` does not use the project's `.python-version`.
  Choose the newest supported interpreter compatible with the branch's Django
  and all release-hook dependencies, and verify the complete command from a
  clean environment. Keep the application matrix checks on their planned
  interpreters, including the transitional Python 3.10 baseline.
- Keep local release preparation non-publishing by default.
- Have the prerelease hook run unit tests, migration checks, lint/static checks,
  and package validation. Add strict documentation and translation validation
  in branches 6a and 6b, including their dependencies in the isolated environment.
- Have the postrelease hook dispatch the trusted publishing workflow through
  `gh`, printing a recoverable manual command if the tag or GitHub
  authentication is unavailable.
- Document the normal sequence: prepare locally, push commits and tag, dispatch
  publication, and verify its result. With automatic pushes disabled, the
  postrelease hook normally prints the manual dispatch command because the tag
  is not yet on GitHub; do not describe that as completed publication.
- Add focused tests for failed prerelease checks, an unpushed tag, unavailable
  GitHub authentication, and dispatch failure without losing the local release.
- Update both `AGENTS.md` and `docs/development.rst` with the final procedure.

### 6a. `upgrade/06a-release-documentation`

- Adapt django-photologue commit
  `4df3862735a2b46fced965df48dac35603a76157` and its later documentation changes,
  rather than copying project-specific paths, theme choices, or service settings.
- Build HTML before release preparation with
  `python -m sphinx -E -W --keep-going -b html docs docs/_build/html`.
  Install documentation dependencies in the isolated release environment and
  keep them compatible with its selected interpreter.
- Make documentation paths independent of the invocation directory. Ensure
  Django initialization does not silence Sphinx warnings, and verify that a
  deliberately introduced warning fails the build.
- Update the existing `.readthedocs.yaml` to install the checked-out project
  and documentation dependencies, select a compatible supported interpreter,
  and fail on warnings. Do not depend on the package already being on PyPI.
- Use Read the Docs' native GitHub integration for release-tag builds. Document
  account-side activation/build rules that match Fiber's actual tag format,
  disable automatic branch/PR builds, and verify `stable` plus a deep-link
  preserving redirect from `latest`. Do not add a custom token-based publisher.
- Verify a manual build of the current implementation commit without publishing
  a package or creating a release tag. Verify versioned documentation and
  aliases at the next permitted release; historical tag rebuilds are out of scope.
- Document independent PyPI and documentation status checks and retries. A
  documentation failure must not cause a successful PyPI upload to be repeated;
  fixes to published tagged source require a new release, not a moved tag.

### 6b. `upgrade/06b-transifex-integration`

- Adapt django-photologue commits
  `91a586048ff9cfa179e19708334e174a921e305d`,
  `131070fef625afd79c9933d75f55d2abee06fb08`, and
  `e27086d69c178b8b3ec157dfc8f412fd6be62860`, reviewing the current files too.
- Configure Transifex's native GitHub integration through `transifex.yml` for
  both existing Fiber resources: `django.po` for Python/templates and
  `djangojs.po` for JavaScript. Preserve the English source catalogues, existing
  translations, resource history, and any required language-code mappings.
- Inspect the existing account/resource configuration before migration. Reuse
  the existing resources rather than creating duplicates; do not copy
  Photologue's resource identifiers or delete catalogues merely because its
  migration removed empty ones. Record any Fiber-specific empty-catalogue
  decisions and retain nonempty translations.
- Keep source strings in Git and translated text in Transifex. Document source
  extraction for both domains, and commit catalogue updates with string changes.
- Batch translation updates into reviewed pull requests, using Photologue's
  all-language grouping and 60-minute interval as the starting settings. Accept
  partial translations and disable Transifex changes to source catalogues.
- Add `bin/compile_translations.py` to validate syntax and format placeholders
  with GNU gettext and compile both domains. Replace each committed `.mo` only
  after its compilation succeeds; review and commit compiled updates before
  merging. Test invalid placeholders and preservation of existing output on
  compilation failure, and verify Python and JavaScript translation loading.
- Run translation validation before release without downloading from Transifex.
  Pending translation PRs, incomplete languages, or Transifex availability must
  not block publication of translations already merged into Git.
- Document service setup, resource preservation, PR review, compilation, and
  recovery. Retire `.tx/config` and obsolete CLI instructions after verifying
  the native mappings. Keep one-time migration details in the implementation
  record and ongoing maintenance instructions in contributor documentation.

### 7. `upgrade/07-django50`

- Move the runtime and test target to the latest Django 5.0 patch on Python
  3.10.
- Review the Django 5.0 release notes and deprecation timeline.
- Update dependency bounds, tox, CI, classifiers, README, and changelog.
- Run tests with warnings enabled and complete the browser acceptance gate.

### 8. `upgrade/08-django51`

- Repeat the release-by-release process for the latest Django 5.1 patch on
  Python 3.10.
- Explicitly verify Fiber authentication and Django REST framework endpoints
  around Django's login middleware behavior.

### 9. `upgrade/09-django52-lts`

- Move to the latest Django 5.2 patch on Python 3.10.
- Set the transitional Django runtime range to `>=5.2,<5.3`.
- Refresh third-party minimums and complete the automated and browser gates.

### 10. `upgrade/10-python311`

- Add Python 3.11 to the Django 5.2 tox and CI matrix.
- Update classifiers and run the complete automated and browser checks under
  Python 3.11.

### 11. `upgrade/11-python312`

- Add Python 3.12 to the Django 5.2 tox and CI matrix.
- Build and install distributions under the lowest and highest supported Python
  versions.

### 12. `upgrade/12-python313`

- Add Python 3.13 to the Django 5.2 tox and CI matrix.
- Update classifiers and run the complete automated and browser checks under
  Python 3.13.

### 13. `upgrade/13-python314`

- Before implementation, require every runtime dependency to declare Python
  3.14 support in a stable release's metadata or documentation. Do not use a
  prerelease or rely only on an empirically passing test suite.
- Add Python 3.14 and remove Python 3.10, producing the final Python 3.11
  through 3.14 and Django 5.2 matrix.
- Raise `requires-python` to `>=3.11`, update `.python-version` to 3.11, and set
  the Django runtime range to `>=5.2.8,<5.3`, because Django 5.2.8 added Python
  3.14 support.
- Update classifiers, README, and changelog; build and install distributions
  under Python 3.11 and 3.14; and complete the browser acceptance gate.
- Treat acceptance of this branch as the backend modernization release gate.

### 14. `upgrade/14-jquery-1x-bridge`

- Upgrade jQuery 1.5.2 to 1.12.4 with uncompressed jQuery Migrate 1.4.1.
- Replace `.live()`, `.andSelf()`, and other reported obsolete APIs in Fiber and
  its vendored or custom plugins.
- Keep Migrate temporarily so manual testing exposes compatibility diagnostics.
- Resolve all reported warnings and remove Migrate before accepting the branch.

### 15. `upgrade/15-jquery-ui`

- Upgrade the milestone jQuery UI 1.9 bundle to jQuery UI 1.14.x.
- Build only the components Fiber uses.
- Adapt the Aristo theme, combobox, dialogs, sortable behavior, menus, and
  flyout extension.
- Manually verify layout, focus, stacking order, drag-and-drop, and context
  menus.

### 16. `upgrade/16-jqtree`

- Upgrade jqTree 0.13 to the latest compatible 1.8.x release.
- Adapt Fiber's tree initialization, events, data loading, and state handling.
- Verify lazy loading, selection, context menus, moving pages and content,
  permissions, and state persistence.

### 17. `upgrade/17-ajax-and-upload`

- Upgrade jQuery Form 2.73 to 4.3.0.
- Upgrade Fine Uploader 3.2.0 to its final 5.16.x release.
- Preserve Fiber's CSRF parameters and existing REST upload contract.
- Test successful uploads, invalid files, server errors, overwrite behavior,
  deletion, progress and cancellation, and both image and file dialogs.

### 18. `upgrade/18-utility-cleanup`

- Remove `jquery.json` in favor of native JSON.
- Replace the dataset helper with standard data APIs.
- Replace `jquery.cookie` with a small supported or native storage
  implementation.
- Retain custom flyout, datagrid, and inheritance code only where necessary,
  porting it to supported jQuery APIs.
- Update or locally replace the slug helper while preserving URL generation.

### 19. `upgrade/19-ckeditor4`

- Rebuild the current CKEditor configuration against CKEditor 4.22.1, the last
  open-source CKEditor 4 release.
- Preserve the current plugin set and Fiber link and image integrations.
- Disable network version checks.
- Document that CKEditor 4.22.1 is an end-of-life compatibility bridge, not a
  secure long-term editor.
- Verify formatting, source mode, links, images, styles, tables, paste,
  fullscreen, dialogs, and saved HTML.

### 20. `upgrade/20-markitup`

- Upgrade the optional MarkItUp bundle from 1.1.10 to 1.1.15.
- Preserve the customized Textile set, icons, image selector, renderer, and URL
  renaming behavior.

### 21. `upgrade/21-jquery3`

- Upgrade from jQuery 1.12.4 to jQuery 3.7.1 with the appropriate jQuery Migrate
  3.x release.
- Resolve all Fiber-owned and vendored-plugin warnings.
- Remove Migrate and rerun the complete frontend checklist.
- Stop at jQuery 3.7.1 for this conservative pass. Evaluate jQuery 4 only after
  obsolete plugins have been removed or replaced.
- Treat acceptance of this branch as the frontend modernization release gate.

## Known blockers and risk decisions

### Django and Python

- Django 4.2, 5.0, and 5.1 are transitional targets because they no longer
  receive security updates. The maintained endpoint is Django 5.2 LTS.
- Python 3.10 is used only as a transitional, `uv`-managed interpreter and
  reaches upstream end of life in October 2026. It is not part of the published
  endpoint.
- django-mptt states that compatibility with new Django versions is maintained.
  Version 0.18 also passed the django-fiber test suite through Django 6.0 during
  planning, so continuing to use it is acceptable. Replacing MPTT is out of
  scope for this modernization.
- At planning time, the stable django-mptt and easy-thumbnails releases did not
  declare Python 3.14 support. Branch 13 is blocked until stable releases of
  every runtime dependency declare that support; passing tests alone do not
  remove this blocker.
- During planning, the Django 4.2 branch plus current compatible dependencies
  also passed all 196 tests on Django 5.0, 5.1, 5.2, and 6.0. These results
  reduce immediate compatibility risk but do not replace the release-by-release
  review and manual checks.

### Frontend

- CKEditor 4 reached end of life in June 2023. Version 4.22.1 is the last
  open-source release and receives no security fixes. CKEditor 5 is not a
  drop-in replacement and is deferred to a separate project.
- Fine Uploader is archived and unmaintained. Moving to its final release
  reduces the age gap but cannot remove the maintenance or security risk.
- MarkItUp, SimpleDataGrid, the flyout extension, and the inheritance helper
  have no actively maintained drop-in successors. Preserve and minimally port
  them rather than combining upgrades with UI redesign.
- jQuery 3.x receives only critical fixes, but it is the safer endpoint for this
  conservative pass. jQuery 4 is a separate breaking-change boundary.

### Packaging and publishing

- Trusted publishing will remain unavailable until maintainers configure the
  GitHub environment and trusted publisher on PyPI. TestPyPI is out of scope.
- Read the Docs and Transifex require account-side integration setup as well as
  repository changes. Record service checks and any pending administrator work
  separately; do not claim a live integration based only on configuration files.
- Release/documentation tools may use newer Python than the transitional local
  baseline only after dependency compatibility and clean-environment checks.
  A tooling interpreter alone does not establish public application support.
- GitHub Actions and third-party action versions must be checked against their
  current stable releases when the workflow branch is implemented.
- Do not publish from the Django 4.2, 5.0, or 5.1 milestones. The intended
  modernization releases follow acceptance of branch 13 for the backend and
  branch 21 for the complete frontend pass.

### Local state

- The local `testproject/testproject_db` must not be reset, deleted, or
  accidentally committed.
- IDE metadata under `.idea/` must remain local.

## Automated validation

Run validation in proportion to each branch, including:

- Django unit tests through the repository wrapper.
- Tests with deprecation warnings enabled.
- `django-admin check` through the test project.
- `makemigrations --check --dry-run`.
- The branch's complete tox and CI matrix.
- Wheel and source distribution build and installation checks.
- `twine check --strict` and manifest validation.
- Strict Sphinx HTML builds and verification that warnings fail the build.
- Translation compilation/format checks for both Python and JavaScript domains,
  plus release-hook failure and publication-retry checks without live uploads.
- Static-file discovery and Django Compressor rendering when frontend assets
  change.
- Review of browser console errors, failed requests, and jQuery Migrate output.

No database schema or public Python API changes are expected. Intentional public
compatibility changes are limited to documented Python and Django requirements,
packaging metadata, and the release process.
Documentation hosting and translation synchronization change operational
procedures, while preserving existing translations and public translation APIs.

## Manual browser acceptance checklist

Complete this checklist after every Django, Python, or JavaScript upgrade branch:

- Start the test project with representative pages, content, images, and files.
- Log in and out through the Fiber overlay.
- Open and close the sidebar; confirm its persisted visibility state.
- Load page and content trees, including their asynchronous data.
- Select, create, edit, reorder, move, and delete pages where permissions allow.
- Drag content items within and between page regions.
- Open page and content context menus and exercise every enabled action.
- Create and edit content through frontend dialogs.
- Verify automatic slug generation and manual slug editing.
- Exercise enhanced select/combobox and structured-data fields.
- Open file and image selectors; search, paginate, select, upload, overwrite,
  cancel, and delete.
- In CKEditor, test text formatting, source mode, links, images, styles, tables,
  paste behavior, fullscreen, save, and reopen.
- When MarkItUp is configured, test formatting, Textile rendering, links, image
  selection, save, and reopen.
- Confirm backend-admin and logout links.
- Confirm there are no unexpected browser console errors, Migrate warnings,
  failed network requests, broken asset paths, or missing images/icons.

The next manual-gated branch must not begin until the current branch's approval
is recorded.
