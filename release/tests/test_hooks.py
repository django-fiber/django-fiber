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
        self.assertEqual(run.call_count, 9)
        self.assertEqual(run.call_args_list[0].args[0],
                         [sys.executable, '-m', 'sphinx', '-E', '-W', '--keep-going',
                          '-b', 'html', 'docs', 'docs/_build/html'])
        self.assertEqual(run.call_args_list[2].args[0], ['sh', './run_tests'])
        for call in run.call_args_list:
            self.assertEqual(call.kwargs['cwd'], '/checkout')
            self.assertTrue(call.kwargs['check'])
            self.assertEqual(call.kwargs['env']['PATH'].split(':')[0], str(Path(sys.executable).parent))
        self.assertEqual(run.call_args_list[-2].args[0][:3], [sys.executable, '-m', 'build'])

    def test_any_failed_check_stops_preparation(self):
        for index in range(9):
            with self.subTest(check=index), patch('release.releaser_hooks.subprocess.run') as run:
                run.side_effect = [None] * index + [subprocess.CalledProcessError(1, 'check')]
                with self.assertRaises(subprocess.CalledProcessError):
                    prereleaser_before({'workingdir': '/checkout'})
                self.assertEqual(run.call_count, index + 1)


class DispatchTests(unittest.TestCase):
    def dispatch(self, results, cli='/usr/bin/gh'):
        from contextlib import redirect_stdout
        import io
        from release.releaser_hooks import trigger_pypi_workflow
        output = io.StringIO()
        with patch('release.releaser_hooks.subprocess.run') as run, patch('shutil.which', return_value=cli):
            run.side_effect = [subprocess.CompletedProcess([], 0, value, '') if isinstance(value, str)
                               else value for value in results]
            with redirect_stdout(output):
                trigger_pypi_workflow({'workingdir': '/checkout'})
        return run, output.getvalue()

    def test_success_dispatches_target_workflow_from_master(self):
        run, output = self.dispatch(['1.11', 'abc', 'abc\trefs/tags/1.11', '', ''])
        self.assertEqual(run.call_args.args[0], ['gh', 'workflow', 'run', 'publish-pypi.yml', '--repo',
                                               'django-fiber/django-fiber', '--ref', 'master',
                                               '-f', 'release_tag=1.11'])
        self.assertIn('verify its result', output)

    def test_missing_tag_preserves_local_release_and_prints_manual_command(self):
        run, output = self.dispatch([subprocess.CalledProcessError(1, 'git', stderr='no tag')])
        self.assertEqual(run.call_count, 1)
        self.assertIn('release_tag=TAG', output)
        self.assertIn('publication was not dispatched', output)

    def test_missing_or_different_remote_tag_does_not_dispatch(self):
        for remote in (subprocess.CalledProcessError(2, 'git'), 'different\trefs/tags/1.11'):
            with self.subTest(remote=remote):
                run, output = self.dispatch(['1.11', 'abc', remote])
                self.assertEqual(run.call_count, 3)
                self.assertIn('release_tag=1.11', output)

    def test_missing_cli_does_not_dispatch(self):
        run, output = self.dispatch(['1.11', 'abc', 'abc\trefs/tags/1.11'], cli=None)
        self.assertEqual(run.call_count, 3)
        self.assertIn('not installed', output)

    def test_authentication_or_dispatch_failure_is_recoverable(self):
        for successful_calls in ([''], []):
            results = ['1.11', 'abc', 'abc\trefs/tags/1.11', *successful_calls,
                       subprocess.CalledProcessError(1, 'gh', stderr='GitHub unavailable')]
            with self.subTest(successful_calls=successful_calls):
                run, output = self.dispatch(results)
                self.assertIn('GitHub unavailable', output)
                self.assertIn('release_tag=1.11', output)
                self.assertIn('publication was not dispatched', output)
