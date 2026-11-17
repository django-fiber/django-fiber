"""Reject changed files before retrying a partially completed PyPI upload."""

import argparse
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import urlopen


def check_existing_files(tag, directory):
    try:
        with urlopen(f'https://pypi.org/pypi/django-fiber/{quote(tag, safe="")}/json', timeout=30) as response:
            uploaded = json.load(response)['urls']
    except HTTPError as error:
        if error.code != 404:
            raise
        uploaded = []
    files = {path.name: path for path in Path(directory).iterdir() if path.is_file()}
    if not files:
        raise ValueError('No distributions to publish')
    for item in uploaded:
        path = files.get(item['filename'])
        if path is None or hashlib.sha256(path.read_bytes()).hexdigest() != item['digests']['sha256']:
            raise ValueError(f'Published file differs from the validated artifact: {item["filename"]}')
    print(f'{len(uploaded)} existing PyPI files match the validated artifact.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tag')
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    check_existing_files(args.tag, args.directory)


if __name__ == '__main__':
    main()
