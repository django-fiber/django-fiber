"""Compiler failures must preserve the last usable translation catalogue."""

import gettext
from pathlib import Path
import subprocess
import tempfile
import unittest

from bin.compile_translations import compile_translations


HEADER = 'msgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8\\n"\n\n'


class TranslationCompilerTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.messages = self.root / 'fr' / 'LC_MESSAGES'
        self.messages.mkdir(parents=True)

    def test_both_domains_load_and_untranslated_strings_fall_back(self):
        for domain in ('django', 'djangojs'):
            (self.messages / f'{domain}.po').write_text(
                HEADER + 'msgid "Hello"\nmsgstr "Bonjour"\n\nmsgid "Untranslated"\nmsgstr ""\n',
                encoding='utf-8',
            )
        compile_translations(self.root)
        for domain in ('django', 'djangojs'):
            with self.subTest(domain=domain):
                translation = gettext.translation(domain, localedir=self.root, languages=['fr'])
                self.assertEqual(translation.gettext('Hello'), 'Bonjour')
                self.assertEqual(translation.gettext('Untranslated'), 'Untranslated')

    def test_syntax_and_placeholder_errors_preserve_existing_output(self):
        for domain in ('django', 'djangojs'):
            for contents in ('malformed catalogue\n', HEADER + '#, python-format\n'
                             'msgid "Hello %(name)s"\nmsgstr "Bonjour %(other)s"\n'):
                with self.subTest(domain=domain, contents=contents):
                    source = self.messages / f'{domain}.po'
                    source.write_text(contents, encoding='utf-8')
                    output = source.with_suffix('.mo')
                    output.write_bytes(b'previous catalogue')
                    with self.assertRaises(subprocess.CalledProcessError):
                        compile_translations(self.root)
                    self.assertEqual(output.read_bytes(), b'previous catalogue')
                    source.unlink()
