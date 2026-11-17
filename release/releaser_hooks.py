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
