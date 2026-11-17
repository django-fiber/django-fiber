import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from release.upload_checks import check_existing_files


class UploadChecksTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        (self.root / 'fiber.whl').write_bytes(b'validated')
        self.item = {'filename': 'fiber.whl', 'digests': {'sha256': hashlib.sha256(b'validated').hexdigest()}}

    def response(self, item):
        return io.BytesIO(json.dumps({'urls': [item]}).encode())

    @patch('release.upload_checks.urlopen')
    def test_matching_partial_upload_is_allowed(self, request):
        request.return_value = self.response(self.item)
        check_existing_files('1.11', self.root)

    @patch('release.upload_checks.urlopen')
    def test_mismatched_or_unexpected_file_is_rejected(self, request):
        for item in (dict(self.item, filename='unexpected.whl'),
                     dict(self.item, digests={'sha256': 'different'})):
            request.return_value = self.response(item)
            with self.subTest(item=item), self.assertRaises(ValueError):
                check_existing_files('1.11', self.root)

    @patch('release.upload_checks.urlopen')
    def test_new_version_is_allowed(self, request):
        request.side_effect = HTTPError('url', 404, 'Not found', {}, None)
        check_existing_files('1.11', self.root)

    @patch('release.upload_checks.urlopen')
    def test_network_or_service_errors_stop_publication(self, request):
        for error in (OSError('offline'), HTTPError('url', 500, 'Unavailable', {}, None)):
            request.side_effect = error
            with self.subTest(error=error), self.assertRaises((OSError, HTTPError)):
                check_existing_files('1.11', self.root)
