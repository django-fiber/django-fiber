"""Checks run by zest.releaser before preparing a release."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile


def prereleaser_before(data):
    """Stop release preparation if any required check fails."""
    root = data['workingdir']
    env = dict(os.environ, PATH=str(Path(sys.executable).parent) + os.pathsep + os.environ.get('PATH', ''))
    commands = [
        [sys.executable, '-m', 'unittest', 'discover', '-s', 'release/tests'],
        ['sh', './run_tests'],
        [sys.executable, 'testproject/manage.py', 'makemigrations', '--check', '--dry-run'],
        [sys.executable, 'testproject/manage.py', 'check'],
        [sys.executable, '-m', 'compileall', '-q', 'fiber', 'release', 'testproject'],
        [sys.executable, '-m', 'check_manifest'],
    ]
    for command in commands:
        print('Checking:', ' '.join(command), flush=True)
        subprocess.run(command, cwd=root, env=env, check=True)
    with tempfile.TemporaryDirectory(prefix='fiber-release-') as directory:
        subprocess.run([sys.executable, '-m', 'build', '--outdir', directory], cwd=root, env=env, check=True)
        distributions = sorted(str(path) for path in Path(directory).iterdir())
        subprocess.run([sys.executable, '-m', 'twine', 'check', '--strict', *distributions],
                       cwd=root, env=env, check=True)


def trigger_pypi_workflow(data):
    """Try dispatching publication without invalidating a completed local release."""
    import shlex
    import shutil

    root = data['workingdir']
    command = ['gh', 'workflow', 'run', 'publish-pypi.yml', '--repo',
               'django-fiber/django-fiber', '--ref', 'master']
    retry = command + ['-f', 'release_tag=TAG']

    def run(arguments):
        return subprocess.run(arguments, cwd=root, check=True, capture_output=True, text=True).stdout.strip()

    try:
        tag = run(['git', 'describe', '--tags', '--exact-match', 'HEAD^'])
        if not tag:
            raise ValueError('No tag found on the release commit preceding the development commit')
        retry = command + ['-f', f'release_tag={tag}']
        local = run(['git', 'rev-parse', f'refs/tags/{tag}'])
        remote = run(['git', 'ls-remote', '--exit-code', '--refs',
                      'https://github.com/django-fiber/django-fiber.git', f'refs/tags/{tag}'])
        if not remote or remote.split()[0] != local:
            raise ValueError('The release tag has not been pushed to the target repository, or differs there')
        if shutil.which('gh') is None:
            raise ValueError('GitHub CLI (gh) is not installed')
        run(['gh', 'auth', 'status', '--hostname', 'github.com'])
        run(retry)
    except (OSError, subprocess.CalledProcessError, ValueError) as error:
        detail = getattr(error, 'stderr', None) or str(error)
        print('Local release preparation completed; publication was not dispatched.')
        print(detail.strip())
        print('After resolving the problem and pushing commits and tag, run:')
        print(shlex.join(retry))
        print('Replace TAG with the release tag if it could not be determined.')
        return
    print(f'Publication workflow dispatched for {tag}; verify its result in GitHub Actions and PyPI.')
