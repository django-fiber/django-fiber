# Contributor and agent guidance

This file applies to the entire repository. Keep changes focused on the issue or
upgrade branch being worked on, and preserve compatibility with the versions in
`tox.ini` unless the change explicitly updates that matrix.

## Project layout

- `fiber/` is the reusable Django application. Python code, migrations,
  templates, translations, and the bundled admin JavaScript and CSS all live
  here.
- `fiber/rest_api/` contains the Django REST framework endpoints used by the
  admin UI.
- `fiber/templates/fiber/` and `fiber/static/fiber/` contain the frontend that
  must be exercised when Django or JavaScript compatibility changes.
- `testproject/` is both the example project and the test harness.
  `testproject/fiber_test/tests/` contains the test suite.
- `docs/` contains the Sphinx documentation. `docs/upgrade-plan.md` is the
  canonical sequence and acceptance policy for the modernization branches.
- `run_tests` and `run_coverage` are the supported local test wrappers.
- `requirements.txt` contains runtime dependencies and
  `test-requirements.txt` contains local test tooling. Packaging metadata is in
  `setup.py` and `setup.cfg` until the packaging upgrade changes it.
- `.github/workflows/` and `tox.ini` define the CI and compatibility matrices.
- `CHANGELOG.rst` records user-visible changes.

Do not commit generated files, virtual environments, coverage or build output,
collected static files, uploaded media, or `testproject/testproject_db`. That
SQLite file is local test-project data and must not be deleted or overwritten
as part of repository cleanup.

## Local environment

Use any environment manager that provides a supported Python interpreter and a
virtual environment. The project commands below do not require `uv`.

For modernization branches that establish Python 3.10 as the local baseline,
this is an optional bootstrap:

```console
uv python install 3.10
uv venv --managed-python --python 3.10 --seed
source .venv/bin/activate
python -m pip install -r requirements.txt -r test-requirements.txt
```

On Windows, activate with `.venv\Scripts\activate` instead. If a root
`.python-version` exists, use the version it names rather than choosing a newer
interpreter implicitly.

## Supported commands

Run commands from the repository root. In particular, do not change into
`testproject/` to invoke its `manage.py`; doing so changes import and database
path behavior.

Run the complete unit suite through the supplied wrapper:

```console
./run_tests
```

The wrapper accepts a test-module suffix for a focused run. For example:

```console
./run_tests test_models
```

This runs `fiber_test.tests.test_models`. Always run `./run_tests` without a
selector before handing off an executable change.

Generate a coverage report with:

```console
./run_coverage
```

Exercise every configured compatibility environment with:

```console
tox
```

When raising the minimum Django version, rewrite all tracked Python files
except migrations with:

```console
python scripts/django_upgrade.py TARGET_VERSION [additional options]
```

For example, target Django 4.2 with
`python scripts/django_upgrade.py 4.2`. Then, when raising the minimum Python
version, run:

```console
python scripts/pyupgrade.py TARGET_FLAG [additional options]
```

For example, target Python 3.10 and later with
`python scripts/pyupgrade.py --py310-plus`. These scripts use `pipx` to run
current versions of the upgrade tools in isolated environments.

Invoke test-project management commands from the root, with the path shown:

```console
python testproject/manage.py <command>
```

Every model or dependency change that could affect model state requires this
migration drift check:

```console
python testproject/manage.py makemigrations --check --dry-run
```

Do not create a migration merely to silence that command. Review any proposed
migration and commit it only when the model-state change is intentional.

Build the documentation, when documentation or public APIs change, with:

```console
python -m sphinx -W -b html docs docs/_build/html
```

## Code and test expectations

- Follow the style of the surrounding code and avoid unrelated formatting or
  refactoring in compatibility changes.
- Add or update focused tests for behavior changes and regressions. Prefer the
  existing Django `TestCase` patterns in `testproject/fiber_test/tests/`.
- Keep migrations compatible with the branch's full Django matrix. Never edit
  an already released migration unless the task specifically requires a
  historical compatibility repair.
- Treat warnings from Fiber-owned code as work to resolve during compatibility
  upgrades; do not hide them with broad warning filters.
- Preserve public APIs and stored HTML unless the change is explicitly
  documented as breaking.
- Changes to bundled JavaScript, CSS, templates, Django/Python versions, or
  frontend dependencies require the manual frontend checklist below.

## Changelog rules

Add a concise entry under the current `(unreleased)` heading in
`CHANGELOG.rst` for user-visible fixes, features, compatibility changes,
deprecations, and removals. Describe the effect on users, not the implementation
process. Keep reStructuredText formatting and the style of nearby entries.

Do not add changelog entries for internal-only test cleanup or documentation
typos unless they materially affect users. Do not create a release heading,
version, or date as part of an ordinary pull request; release tooling owns that
transition. Keep compatibility claims synchronized across the changelog,
README, package metadata, tox, and CI.

## Compatibility-upgrade runbook

For each Django, Python, or dependency compatibility branch:

1. Confirm the branch base and scope against `docs/upgrade-plan.md`. Keep the
   numbered branches linear and do not pull work from a later branch forward.
2. Read the upstream release notes, supported-version tables, deprecation
   timeline, and the release notes for relevant third-party dependencies.
3. When raising the minimum Django version, run `django-upgrade` for the new
   target before manual compatibility changes. When raising the minimum Python
   version, run `pyupgrade` with the corresponding minimum-version flag after
   `django-upgrade`. Run both tools across all tracked Python files except files
   in migration directories, then format the changed code. Review the diffs and
   commit each mechanical transformation separately before making manual
   compatibility changes.
4. Update dependency bounds, tox, CI, package classifiers and metadata,
   `.python-version` when applicable, README compatibility statements, and the
   changelog as one consistent set.
5. Install both the lowest permitted and intended/current dependency versions
   where practical. Do not claim support based only on an unconstrained local
   environment.
6. Run focused tests while developing, then the full `./run_tests` wrapper,
   `python testproject/manage.py makemigrations --check --dry-run`, and all
   applicable tox environments with warnings enabled. Run the migration check
   after automated upgrades even though migration files are excluded, because
   changes to model declarations can still require migrations.
7. For packaging changes, build both wheel and source distribution and inspect
   their contents. For Django, Python, template, static, or JavaScript changes,
   complete the manual frontend checklist.
8. Record exact commands, environments, results, warnings, manual checks,
   blockers, and deviations in the pull request. Update the upgrade plan if an
   implementation finding changes an agreed target or sequence.

Treat `django-upgrade` and `pyupgrade` as aids rather than proof of
compatibility. Their output requires review, and the complete automated and
manual acceptance checks still apply.

Do not publish from a transitional modernization branch. Publication gates are
defined in `docs/upgrade-plan.md`.

## Manual frontend checklist

Use a fresh local database or a backed-up disposable copy; never replace a
developer's `testproject/testproject_db`. Start the project from the repository
root:

```console
python testproject/manage.py migrate
python testproject/manage.py createsuperuser
python testproject/manage.py runserver
```

Test with browser developer tools open and report JavaScript errors, warnings,
failed requests, and server tracebacks. At minimum verify:

- authentication: log in and out, load a Fiber-enabled page, and confirm that
  anonymous users cannot access admin/API actions;
- page tree: load and expand it, select pages, create/edit/delete a disposable
  page, reorder or move it, and confirm the state and hierarchy persist after a
  refresh;
- page editing: edit titles, URLs, metadata and content; verify validation,
  redirects/refreshes, and rendered output;
- content items: open inline and dialog editors, create/edit/delete disposable
  content, and exercise double-click and context-menu actions;
- rich-text editing: format text, switch source mode, add and edit links,
  images, lists and tables, paste content, use fullscreen, save, reopen, and
  confirm the stored/rendered HTML remains intact;
- files and images: open selectors, upload a valid file and image, observe
  progress, choose existing assets, verify previews/thumbnails, and exercise a
  validation or server-error path when the branch touches uploads;
- frontend behavior: dialogs open and close, menus and flyouts position
  correctly, drag-and-drop and sortable controls work, focus/keyboard behavior
  is usable, and overlays have the correct stacking order;
- API/network behavior: page, content, file and image requests return expected
  statuses and retain CSRF protection; and
- presentation: check the public page and Fiber UI at common desktop widths,
  with no obvious layout, icon, or static-asset regressions.

For a narrowly scoped change, emphasize affected paths, but complete the full
checklist on every Django, Python, or JavaScript upgrade branch. Record browser,
OS, Python/Django versions, and the result in the pull request.

## Pull-request expectations

- Keep one upgrade-plan section per branch and base it on the predecessor
  specified by the plan. Do not begin the next branch before its prerequisite
  is accepted.
- Explain the user-visible outcome, compatibility impact, and important design
  choices. Call out migrations, dependency-bound changes, vendored assets, and
  release implications explicitly.
- List automated commands and their results. Never write only "tests pass";
  identify the wrapper/tox environments and migration check that ran.
- Include the completed manual checklist, or state why it is not applicable.
  For UI changes, attach useful screenshots or recordings and browser-console
  findings.
- Identify known warnings, skipped environments, blockers, deviations from the
  plan, and follow-up work. Do not silently reduce the supported matrix or
  acceptance checks.
- Keep generated artifacts and local test-project data out of the diff, and
  review the final diff for unrelated changes before requesting review.
