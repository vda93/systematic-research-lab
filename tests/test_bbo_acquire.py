"""Network-free acquisition controls; tiny original gzip fixtures, no provider rows."""
from contextlib import ExitStack
from datetime import date
import gzip
import hashlib
import importlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError


def api():
    try:
        module = importlib.import_module('srl.bbo_acquire')
    except ModuleNotFoundError:
        module = None
    assert module is not None, 'bounded acquisition controls have not been implemented'
    return module


class Response(io.BytesIO):
    def __init__(self, payload, url, *, status=200, headers=None, fail_read=False):
        super().__init__(payload)
        self.status, self.url = status, url
        self.headers = headers if headers is not None else {'Content-Length': str(len(payload)), 'ETag': 'fixture'}
        self.fail_read = fail_read

    def geturl(self):
        return self.url

    def read(self, size=-1):
        if not 0 < size <= 4 * 1024 * 1024:
            raise AssertionError('every read must be bounded to at most 4 MiB')
        if self.fail_read and self.tell():
            raise TimeoutError('synthetic interrupted stream')
        return super().read(size)


class ImportContractTests(unittest.TestCase):
    def test_acquisition_api_is_implemented(self):
        self.assertTrue(callable(api().download_day))


class AcquisitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.module = api()
        except AssertionError:
            raise unittest.SkipTest('implementation absent; import contract test supplies the failure')

    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.base = Path(self.scratch.name)
        self.root, self.cache = self.base / 'source', self.base / 'cache'
        self.root.mkdir()
        (self.root / 'experiments').mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Synthetic fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        (self.root / 'experiments/bbo-delay-protocol.md').write_bytes(b'original synthetic protocol\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'synthetic protocol')
        original = self.git('rev-parse', 'HEAD').strip()
        (self.root / 'experiments/bbo-delay-measurement-v2.md').write_bytes(b'synthetic measurement amendment\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'synthetic amendment')
        self.commit = self.git('rev-parse', 'HEAD').strip()
        self.payload = gzip.compress(b'original integrity fixture; no market observations\n', mtime=0)
        self.calls, self.sleeps = [], []
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(self.module, 'ROOT', self.root))
        self.stack.enter_context(patch.object(self.module, 'BASE_PROTOCOL_COMMIT', original))
        self.stack.enter_context(patch.object(self.module, '_open', self.open))
        self.stack.enter_context(patch.object(self.module, '_sleep', self.sleeps.append))
        self.stack.enter_context(patch.object(self.module.shutil, 'disk_usage', return_value=SimpleNamespace(free=30 * 1024**3)))
        self.actions = []

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], check=True, capture_output=True, text=True).stdout

    def open(self, request, *, timeout):
        self.calls.append(request)
        self.assertLessEqual(timeout, 60)
        if self.actions:
            action = self.actions.pop(0)
            if isinstance(action, Exception):
                raise action
            return action
        return Response(self.payload, request.full_url)

    def run_download(self, **kwargs):
        return self.module.download_day('2023-01-01', self.cache, protocol_commit=self.commit, **kwargs)

    def test_complete_crc_hash_and_verified_reuse_without_second_request(self):
        receipt = self.run_download()
        self.assertEqual(receipt['status'], 'COMPLETE')
        target = Path(receipt['path'])
        self.assertEqual(target.read_bytes(), self.payload)
        self.assertEqual(receipt['sha256'], hashlib.sha256(self.payload).hexdigest())
        self.assertTrue(receipt['gzip_crc_verified'])
        self.assertEqual(json.loads(Path(receipt['receipt_path']).read_text())['status'], 'COMPLETE')
        self.assertEqual(self.run_download()['status'], 'REUSED_VERIFIED')
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.calls[0].full_url, 'https://datasets.tardis.dev/v1/binance/book_ticker/2023/01/01/BTCUSDT.csv.gz')
        self.assertNotIn('Authorization', self.calls[0].headers)
        self.assertIn('systematic-research-lab', self.calls[0].headers['User-agent'])

    def test_protocol_must_be_real_committed_current_amendment(self):
        for bad in ['main', 'f' * 40, self.git('rev-parse', 'HEAD^').strip()]:
            receipt = self.module.download_day('2023-01-01', self.cache, protocol_commit=bad)
            self.assertEqual(receipt['status'], 'NOT_RUN_PROTOCOL')
        (self.root / 'experiments/bbo-delay-measurement-v2.md').write_text('uncommitted changed amendment')
        self.assertEqual(self.run_download()['status'], 'NOT_RUN_PROTOCOL')
        self.assertEqual(self.calls, [])

    def test_only_fixed_dates_and_explicit_matching_later_year_are_allowed(self):
        for bad in ['2023-01-02', '2026-01-01', '2023-1-01', '../2023-01-01']:
            self.assertEqual(self.module.download_day(bad, self.cache, protocol_commit=self.commit)['status'], 'NOT_RUN_DATE')
        self.assertEqual(self.module.download_day('2024-01-01', self.cache, protocol_commit=self.commit)['status'], 'NOT_RUN_STAGE')
        later = self.module.download_day(date(2024, 1, 1), self.cache, protocol_commit=self.commit, allow_year=2024)
        self.assertEqual(later['status'], 'COMPLETE')
        self.assertEqual(later['stage_authorization'], 'CALLER_EXPLICIT_YEAR_ONLY')

    def test_in_repository_and_symlinked_cache_are_rejected_before_request(self):
        self.assertEqual(self.module.download_day('2023-01-01', self.root / 'build/raw', protocol_commit=self.commit)['status'], 'NOT_RUN_CACHE')
        self.assertFalse((self.root / 'build').exists())
        other = self.base / 'another-git'
        other.mkdir()
        subprocess.run(['git', '-C', str(other), 'init', '-q'], check=True, capture_output=True)
        self.assertEqual(self.module.download_day('2023-01-01', other / 'raw', protocol_commit=self.commit)['status'], 'NOT_RUN_CACHE')
        linked = self.base / 'linked'
        try:
            linked.symlink_to(self.root, target_is_directory=True)
        except OSError:
            return  # Windows may disallow symlinks; Git-root rejection above still executes.
        self.assertEqual(self.module.download_day('2023-01-01', linked / 'raw', protocol_commit=self.commit)['status'], 'NOT_RUN_CACHE')
        self.assertEqual(self.calls, [])

    def test_existing_unreceipted_or_partial_source_is_never_replaced(self):
        self.cache.mkdir()
        target = self.cache / 'binance_book_ticker_2023-01-01_BTCUSDT.csv.gz'
        target.write_bytes(b'preserve unknown source')
        self.assertEqual(self.run_download()['status'], 'NOT_RUN_EXISTING')
        self.assertEqual(target.read_bytes(), b'preserve unknown source')
        target.unlink()
        partial = Path(str(target) + '.partial')
        partial.write_bytes(b'preserve interrupted source')
        self.assertEqual(self.run_download()['status'], 'NOT_RUN_EXISTING')
        self.assertEqual(partial.read_bytes(), b'preserve interrupted source')
        self.assertEqual(self.calls, [])

    def test_changed_reuse_hash_and_expected_hash_fail_closed(self):
        receipt = self.run_download()
        target = Path(receipt['path'])
        original_receipt = Path(receipt['receipt_path']).read_bytes()
        target.write_bytes(b'changed')
        self.assertEqual(self.run_download()['status'], 'FAIL_INTEGRITY')
        self.assertEqual(Path(receipt['receipt_path']).read_bytes(), original_receipt)
        self.assertEqual(len(self.calls), 1)

    def test_expected_hash_mismatch_preserves_partial_and_error_receipt(self):
        receipt = self.run_download(expected_sha256='0' * 64)
        self.assertEqual(receipt['status'], 'FAIL_INTEGRITY')
        self.assertTrue(Path(receipt['partial_path']).exists())
        self.assertFalse(Path(receipt['path']).exists())
        self.assertEqual(json.loads(Path(receipt['receipt_path']).read_text())['status'], 'FAIL_INTEGRITY')

    def test_corrupt_and_truncated_gzip_fail_without_final_file(self):
        self.payload = self.payload[:-4]
        receipt = self.run_download()
        self.assertEqual(receipt['status'], 'FAIL_INTEGRITY')
        self.assertFalse(Path(receipt['path']).exists())
        self.assertFalse(receipt['gzip_crc_verified'])

    def test_transient_open_errors_retry_three_attempts_with_two_four_backoff(self):
        self.actions = [URLError('synthetic network'), HTTPError('synthetic', 503, 'retry', {}, None)]
        self.assertEqual(self.run_download()['status'], 'COMPLETE')
        self.assertEqual(len(self.calls), 3)
        self.assertEqual(self.sleeps, [2, 4])

    def test_access_errors_and_redirects_stop_without_retry(self):
        for status in [401, 403, 404, 429, 302, 204]:
            with self.subTest(status=status), tempfile.TemporaryDirectory() as destination:
                self.actions = [HTTPError('synthetic', status, 'stop', {}, None)]
                receipt = self.module.download_day('2023-01-01', destination, protocol_commit=self.commit)
                self.assertNotEqual(receipt['status'], 'COMPLETE')
                self.assertEqual(receipt['attempts'][-1]['http_status'], status)
        self.assertEqual(len(self.calls), 6)
        self.assertEqual(self.sleeps, [])

    def test_read_timeout_preserves_atomic_checkpoint_and_does_not_restart_body(self):
        self.actions = [Response(self.payload, 'https://datasets.tardis.dev/v1/binance/book_ticker/2023/01/01/BTCUSDT.csv.gz', fail_read=True)]
        receipt = self.run_download()
        self.assertEqual(receipt['status'], 'INCOMPLETE_TRANSPORT')
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(Path(receipt['partial_path']).read_bytes(), self.payload)
        self.assertEqual(json.loads(Path(receipt['receipt_path']).read_text())['status'], 'INCOMPLETE_TRANSPORT')

    def test_reuse_still_respects_total_retained_cap(self):
        receipt = self.run_download()
        with patch.object(self.module, '_LIMITS', self.module._Limits(total_bytes=1)):
            self.assertEqual(self.run_download()['status'], 'NOT_RUN_RESOURCE')
        self.assertEqual(len(self.calls), 1)
        self.assertTrue(Path(receipt['path']).exists())
    def test_empty_body_is_not_falsely_marked_crc_verified(self):
        self.payload = b''
        receipt = self.run_download()
        self.assertEqual(receipt['status'], 'FAIL_INTEGRITY')
        self.assertFalse(receipt['gzip_crc_verified'])

    def test_lock_and_prior_error_receipt_are_preserved(self):
        self.cache.mkdir()
        lock = self.cache / '.bbo-acquisition.lock'
        lock.write_bytes(b'prior worker ownership')
        self.assertEqual(self.run_download()['status'], 'NOT_RUN_CONCURRENT')
        self.assertEqual(lock.read_bytes(), b'prior worker ownership')
        self.assertEqual(self.calls, [])

    def test_stream_without_length_cannot_exceed_file_cap(self):
        self.actions = [Response(self.payload, 'https://datasets.tardis.dev/v1/binance/book_ticker/2023/01/01/BTCUSDT.csv.gz', headers={})]
        with patch.object(self.module, '_LIMITS', self.module._Limits(file_bytes=10, total_bytes=1000, reserve_bytes=10, elapsed_seconds=10)):
            receipt = self.run_download()
        self.assertEqual(receipt['status'], 'INCOMPLETE_RESOURCE')
        self.assertFalse(Path(receipt['path']).exists())
        self.assertTrue(Path(receipt['partial_path']).exists())
        self.assertEqual(len(self.calls), 1)

    def test_failed_open_attempts_are_bounded_and_receipted(self):
        self.actions = [URLError('fixture')] * 4
        receipt = self.run_download()
        self.assertEqual(receipt['status'], 'INCOMPLETE_TRANSPORT')
        self.assertEqual(len(self.calls), 3)
        self.assertEqual(self.sleeps, [2, 4])
        self.assertEqual(len(receipt['attempts']), 3)
        self.assertEqual(json.loads(Path(receipt['receipt_path']).read_text())['status'], 'INCOMPLETE_TRANSPORT')
    def test_file_total_disk_and_elapsed_caps_fail_closed(self):
        limits = self.module._Limits(file_bytes=10, total_bytes=100, reserve_bytes=10, elapsed_seconds=10)
        with patch.object(self.module, '_LIMITS', limits):
            self.assertEqual(self.run_download()['status'], 'NOT_RUN_RESOURCE')
        self.assertEqual(len(self.calls), 1)  # Header rejected before body allocation.
        with tempfile.TemporaryDirectory() as destination:
            Path(destination, 'retained.bin').write_bytes(b'x' * 96)
            with patch.object(self.module, '_LIMITS', self.module._Limits(file_bytes=10, total_bytes=100, reserve_bytes=10, elapsed_seconds=10)):
                receipt = self.module.download_day('2023-01-01', destination, protocol_commit=self.commit)
                self.assertEqual(receipt['status'], 'NOT_RUN_RESOURCE')
        with tempfile.TemporaryDirectory() as destination, patch.object(self.module.shutil, 'disk_usage', return_value=SimpleNamespace(free=6 * 1024**3)):
            self.assertEqual(self.module.download_day('2023-01-01', destination, protocol_commit=self.commit)['status'], 'NOT_RUN_RESOURCE')
        with tempfile.TemporaryDirectory() as destination, patch.object(self.module, '_clock', side_effect=[0, 7201, 7201, 7201]):
            self.assertEqual(self.module.download_day('2023-01-01', destination, protocol_commit=self.commit)['status'], 'NOT_RUN_RESOURCE')


if __name__ == '__main__':
    unittest.main()
