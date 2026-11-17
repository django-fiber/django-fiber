"""Release checks must fail before any release commit or tag is prepared."""

from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from release.releaser_hooks import prereleaser_before


class PrereleaseTests(unittest.TestCase):
    @patch('release.releaser_hooks.subprocess.run')
    def test_checks_use_root_and_current_interpreter(self, run):
        prereleaser_before({'workingdir': '/checkout'})
        self.assertEqual(run.call_count, 8)
        self.assertEqual(run.call_args_list[1].args[0], ['sh', './run_tests'])
        for call in run.call_args_list:
            self.assertEqual(call.kwargs['cwd'], '/checkout')
            self.assertTrue(call.kwargs['check'])
            self.assertEqual(call.kwargs['env']['PATH'].split(':')[0], str(Path(sys.executable).parent))
        self.assertEqual(run.call_args_list[-2].args[0][:3], [sys.executable, '-m', 'build'])

    def test_any_failed_check_stops_preparation(self):
        for index in range(8):
            with self.subTest(check=index), patch('release.releaser_hooks.subprocess.run') as run:
                run.side_effect = [None] * index + [subprocess.CalledProcessError(1, 'check')]
                with self.assertRaises(subprocess.CalledProcessError):
                    prereleaser_before({'workingdir': '/checkout'})
                self.assertEqual(run.call_count, index + 1)
