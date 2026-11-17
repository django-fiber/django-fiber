"""Sphinx must keep reporting warnings after the Django configuration loads."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


class DocumentationTests(unittest.TestCase):
    def test_documentation_builds_from_another_directory_and_warnings_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source'
            source.mkdir()
            for warning in (False, True):
                with self.subTest(warning=warning):
                    contents = 'Documentation check\n===================\n\nValid text.\n'
                    if warning:
                        contents += '\nSee :ref:`fiber-warning-probe`.\n'
                    (source / 'index.rst').write_text(contents, encoding='utf-8')
                    # Keep the regression independent of remote intersphinx inventories.
                    result = subprocess.run(
                        [sys.executable, '-m', 'sphinx', '-E', '-W', '--keep-going',
                         '-D', 'extensions=sphinx.ext.todo', '-b', 'html', '-c', str(ROOT / 'docs'),
                         str(source), str(root / 'output')],
                        cwd=root, capture_output=True, text=True,
                    )
                    if warning:
                        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                        self.assertIn('undefined label', result.stdout + result.stderr)
                        self.assertIn('fiber-warning-probe', result.stdout + result.stderr)
                    else:
                        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
