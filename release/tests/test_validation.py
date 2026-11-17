"""Exercise release validation using real disposable Git histories and archives."""

import io
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
import zipfile

from release.validation import validate_distributions, validate_tag


class TagTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.git('init', '-q')
        self.git('config', 'user.name', 'Release tests')
        self.git('config', 'user.email', 'tests@example.invalid')
        (self.root / 'fiber').mkdir()
        (self.root / 'fiber/__init__.py').write_text("__version__ = '1.11'\n")
        self.git('add', '.')
        self.git('commit', '-qm', 'Release')
        self.git('tag', '1.11')
        self.git('update-ref', 'refs/remotes/origin/master', 'HEAD')

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, text=True).strip()

    def test_valid_tag(self):
        validate_tag('1.11', self.root)

    def test_invalid_or_mismatched_version(self):
        for tag in ('invalid', '1.11.dev1', '1.11+local', '1.12'):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                validate_tag(tag, self.root)

    def test_checkout_must_match_tag(self):
        self.git('commit', '--allow-empty', '-qm', 'Later')
        with self.assertRaisesRegex(ValueError, 'Checkout'):
            validate_tag('1.11', self.root)

    def test_unmerged_tag_is_rejected(self):
        self.git('checkout', '--orphan', 'unrelated')
        self.git('commit', '--allow-empty', '-qm', 'Unrelated')
        self.git('update-ref', 'refs/remotes/origin/master', 'HEAD')
        self.git('checkout', '--detach', '1.11')
        with self.assertRaises(subprocess.CalledProcessError):
            validate_tag('1.11', self.root)


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def distributions(self, wheel_version='1.11', source_version='1.11', name='django-fiber'):
        def metadata(version):
            return f'Metadata-Version: 2.4\nName: {name}\nVersion: {version}\n'.encode()
        with zipfile.ZipFile(self.root / 'fiber.whl', 'w') as archive:
            archive.writestr('fiber.dist-info/METADATA', metadata(wheel_version))
        with tarfile.open(self.root / 'fiber.tar.gz', 'w:gz') as archive:
            contents = metadata(source_version)
            member = tarfile.TarInfo('fiber/PKG-INFO')
            member.size = len(contents)
            archive.addfile(member, io.BytesIO(contents))

    def test_matching_distributions(self):
        self.distributions()
        validate_distributions('1.11', self.root)

    def test_either_version_mismatch_is_rejected(self):
        for versions in (('1.12', '1.11'), ('1.11', '1.12')):
            self.distributions(*versions)
            with self.subTest(versions=versions), self.assertRaisesRegex(ValueError, 'version'):
                validate_distributions('1.11', self.root)

    def test_wrong_project_is_rejected(self):
        self.distributions(name='other-project')
        with self.assertRaisesRegex(ValueError, 'name'):
            validate_distributions('1.11', self.root)

    def test_missing_or_stale_files_are_rejected(self):
        with self.assertRaises(ValueError):
            validate_distributions('1.11', self.root)
        self.distributions()
        (self.root / 'stale.whl').touch()
        with self.assertRaises(ValueError):
            validate_distributions('1.11', self.root)
