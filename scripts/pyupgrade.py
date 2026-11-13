#!/usr/bin/env python3

import os
import subprocess
import sys


def main():
    if len(sys.argv) < 2:
        print(
            f'Usage: {sys.argv[0]} TARGET_FLAG [additional options]',
            file=sys.stderr,
        )
        return 2

    target_flag, *additional_options = sys.argv[1:]
    repository_root = os.fsdecode(subprocess.run(
        ['git', 'rev-parse', '--show-toplevel'],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout.rstrip(b'\n'))
    python_files = [
        os.fsdecode(path)
        for path in subprocess.run(
            [
                'git', 'ls-files', '-z', '--', '*.py',
                ':(exclude,glob)**/migrations/**',
            ],
            check=True,
            cwd=repository_root,
            stdout=subprocess.PIPE,
        ).stdout.split(b'\0')
        if path
    ]

    return subprocess.call(
        [
            sys.executable, '-m', 'pipx', 'run', '--refresh',
            'pyupgrade', '--exit-zero-even-if-changed', target_flag,
            *additional_options,
            *python_files,
        ],
        cwd=repository_root,
    )


if __name__ == '__main__':
    raise SystemExit(main())
