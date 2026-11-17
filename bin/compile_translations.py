#!/usr/bin/env python
"""Validate and compile both Fiber gettext domains with GNU gettext."""

from pathlib import Path
import subprocess
import tempfile


def compile_translations(locale_dir):
    for domain in ('django', 'djangojs'):
        for source in sorted(Path(locale_dir).glob(f'*/LC_MESSAGES/{domain}.po')):
            # Keep the existing catalogue until this file compiles successfully.
            with tempfile.TemporaryDirectory(dir=source.parent) as directory:
                output = Path(directory) / f'{domain}.mo'
                subprocess.run(['msgfmt', '--check-format', '-o', str(output), str(source)], check=True)
                output.replace(source.with_suffix('.mo'))


if __name__ == '__main__':
    compile_translations(Path(__file__).resolve().parents[1] / 'fiber' / 'locale')
