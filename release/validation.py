"""Validate tagged source and built distribution metadata before publication."""

import argparse
import ast
from email.parser import BytesParser
from pathlib import Path
import subprocess
import tarfile
import zipfile

from packaging.utils import canonicalize_name
from packaging.version import Version


def validate_tag(tag, root=Path('.')):
    version = Version(tag)
    if version.is_devrelease or version.local:
        raise ValueError('Development and local versions cannot be published')
    tree = ast.parse((root / 'fiber/__init__.py').read_text(encoding='utf-8'))
    versions = [ast.literal_eval(node.value) for node in tree.body
                if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == '__version__' for target in node.targets)]
    if versions != [tag]:
        raise ValueError('Tag must exactly match fiber.__version__')
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=root, text=True).strip()
    if git('rev-parse', f'refs/tags/{tag}^{{commit}}') != git('rev-parse', 'HEAD'):
        raise ValueError('Checkout does not match the release tag')
    subprocess.run(['git', 'merge-base', '--is-ancestor', 'HEAD', 'refs/remotes/origin/master'],
                   cwd=root, check=True)


def validate_distributions(tag, directory):
    files = sorted(Path(directory).iterdir())
    wheels = [path for path in files if path.suffix == '.whl']
    sources = [path for path in files if path.name.endswith('.tar.gz')]
    if len(files) != 2 or len(wheels) != 1 or len(sources) != 1:
        raise ValueError('Expected exactly one wheel and one source distribution')
    with zipfile.ZipFile(wheels[0]) as archive:
        names = [name for name in archive.namelist() if name.endswith('.dist-info/METADATA')]
        if len(names) != 1:
            raise ValueError('Expected one wheel metadata file')
        wheel_metadata = archive.read(names[0])
    with tarfile.open(sources[0]) as archive:
        members = [member for member in archive.getmembers()
                   if member.isfile() and len(member.name.split('/')) == 2 and member.name.endswith('/PKG-INFO')]
        if len(members) != 1:
            raise ValueError('Expected one source metadata file')
        source_metadata = archive.extractfile(members[0]).read()
    for contents in (wheel_metadata, source_metadata):
        metadata = BytesParser().parsebytes(contents)
        if canonicalize_name(metadata.get('Name', '')) != 'django-fiber':
            raise ValueError('Wrong distribution project name')
        if Version(metadata.get('Version', '')) != Version(tag):
            raise ValueError('Distribution version does not match tag')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tag')
    parser.add_argument('--dist', type=Path)
    args = parser.parse_args()
    validate_tag(args.tag)
    if args.dist:
        validate_distributions(args.tag, args.dist)


if __name__ == '__main__':
    main()
