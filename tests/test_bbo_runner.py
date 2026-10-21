"""Private-output and stage guards using an original synthetic gzip file."""
import gzip
import hashlib
import importlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

FREEZE = '76c8952ac6a18b6ab167878974f9cf2b4bad89c9'


def api():
    try:
        module = importlib.import_module('srl.bbo_runner')
    except ModuleNotFoundError:
        module = None
    assert module is not None, 'private, staged day replay runner is not implemented'
    return module


class RunnerTests(unittest.TestCase):
    def test_native_peak_memory_normalizes_platform_units_and_fails_closed(self):
        import ctypes
        import sys
        module = api()
        resource = SimpleNamespace(RUSAGE_SELF=0, getrusage=lambda who: SimpleNamespace(ru_maxrss=123))
        with patch.dict(sys.modules, {'resource': resource}):
            with patch.object(sys, 'platform', 'linux'):
                self.assertEqual(module._rss(), 125952)
            with patch.object(sys, 'platform', 'darwin'):
                self.assertEqual(module._rss(), 123)
        def measure(process, pointer, size):
            self.assertEqual(process, 42)
            self.assertEqual(size, pointer._obj.cb)
            pointer._obj.PeakWorkingSetSize = 654321
            pointer._obj.WorkingSetSize = 123
            return 1
        native = SimpleNamespace(kernel32=SimpleNamespace(GetCurrentProcess=lambda: 42),
                                 psapi=SimpleNamespace(GetProcessMemoryInfo=measure))
        with patch.object(sys, 'platform', 'win32'), patch.object(ctypes, 'windll', native, create=True):
            self.assertEqual(module._rss(), 654321)
            native.psapi.GetProcessMemoryInfo = lambda *args: 0
            with self.assertRaises(OSError):
                module._rss()

    def test_validation_path_requires_stage_proof_and_records_it_before_replay(self):
        module = api()
        self.assertTrue(hasattr(module, 'verify_stage'), 'worker stage guard is not integrated')
        payload = gzip.compress(b'exchange,symbol,timestamp,local_timestamp,ask_amount,ask_price,bid_price,bid_amount\n', mtime=0)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = root/'fixture.csv.gz'
            raw.write_bytes(payload)
            proof = dict(stage='VALIDATION', verification='ORIGINAL_SYNTHETIC_BOUNDARY_FIXTURE')
            def local_blob(source_root, command, reference):
                self.assertEqual(command, 'show')
                return (source_root/reference.split(':',1)[1]).read_bytes()
            # Freeze and guard semantics have real temporary-Git tests separately.
            # Here isolate their boundary and exercise actual worker/replay/output.
            with patch.object(module, 'verify_stage', return_value=proof) as guard, patch.object(module, '_git', side_effect=local_blob):
                receipt = module.run_day(raw, day='2024-01-01', output=root/'run', protocol_commit=FREEZE,
                                         expected_sha256=hashlib.sha256(payload).hexdigest(),
                                         implementation_commit='1'*40, stage_commit='2'*40)
            guard.assert_called_once_with(module.ROOT, day='2024-01-01', implementation_commit='1'*40,
                                          stage_commit='2'*40)
            self.assertEqual(receipt['status'], 'COMPLETE')
            self.assertEqual(receipt['stage_proof'], proof)

    def test_post_report_io_cap_and_memory_failures_never_leave_a_completed_report(self):
        from srl.bbo_replay import DayReplay
        def synthetic_replay(updates, *, start_us, audit):
            list(updates)
            audit({'intent_us': start_us+300_000_000, 'side': 1, 'synthetic': True})
            return DayReplay({'scheduled_intents': 1, 'synthetic_padding': 'x'*220000}, {})

        payload = gzip.compress(b'exchange,symbol,timestamp,local_timestamp,ask_amount,ask_price,bid_price,bid_amount\n', mtime=0)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = root/'fixture.csv.gz'
            raw.write_bytes(payload)
            module = api()
            actual_hash = module._hash
            def fail_artifact(path, *args, **kwargs):
                if path.name == 'audit.jsonl.gz':
                    raise OSError('synthetic artifact hash failure')
                return actual_hash(path, *args, **kwargs)
            contexts = [patch.object(module, '_hash', side_effect=fail_artifact),
                        patch.object(module, 'OUTPUT_CAP', 100000),
                        patch.object(module, 'replay_updates', side_effect=MemoryError('synthetic memory failure'))]
            for index, context in enumerate(contexts):
                with self.subTest(case=index), patch.object(module, 'replay_updates', synthetic_replay), context:
                    output = root/str(index)
                    receipt = module.run_day(raw, day='2023-01-01', output=output, protocol_commit=FREEZE,
                                             expected_sha256=hashlib.sha256(payload).hexdigest())
                    self.assertEqual(receipt['status'], 'FAILED')
                    self.assertEqual(json.loads((output/'receipt.json').read_text())['status'], 'FAILED')
                    self.assertFalse((output/'report.json').exists())

    def test_cli_runs_offline_and_returns_failure_exit_code(self):
        import subprocess
        import sys
        script = Path(__file__).resolve().parents[1]/'scripts/bbo_run_day.py'
        self.assertTrue(script.is_file(), 'explicit offline replay CLI is missing')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = root/'fixture.csv.gz'
            raw.write_bytes(b'wrong original fixture')
            result = subprocess.run([sys.executable, str(script), '--day', '2023-01-01',
                                     '--raw', str(raw), '--output', str(root/'run'),
                                     '--protocol-commit', FREEZE, '--sha256', '0'*64],
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)['status'], 'FAILED')

    def test_corrupt_gzip_cannot_publish_prefix_and_resource_stop_retains_failure(self):
        payload = gzip.compress(b'exchange,symbol,timestamp,local_timestamp,ask_amount,ask_price,bid_price,bid_amount\n', mtime=0)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = root/'corrupt.csv.gz'
            raw.write_bytes(payload[:-5])
            receipt = api().run_day(raw, day='2023-01-01', output=root/'crc', protocol_commit=FREEZE,
                                   expected_sha256=hashlib.sha256(raw.read_bytes()).hexdigest())
            self.assertEqual(receipt['status'], 'FAILED')
            self.assertFalse((root/'crc/report.json').exists())
            raw.write_bytes(payload)
            with patch.object(api(), '_rss', return_value=3*1024**3):
                receipt = api().run_day(raw, day='2023-01-01', output=root/'memory', protocol_commit=FREEZE,
                                       expected_sha256=hashlib.sha256(payload).hexdigest())
            self.assertEqual(receipt['status'], 'FAILED')
            self.assertFalse((root/'memory/report.json').exists())
            self.assertEqual(json.loads((root/'memory/receipt.json').read_text())['status'], 'FAILED')

    def test_resource_stop_bounds_raw_work_inside_equal_timestamp_group(self):
        header = b'exchange,symbol,timestamp,local_timestamp,ask_amount,ask_price,bid_price,bid_amount\n'
        row = b'binance,BTCUSDT,1672531200000000,1672531200000000,2,101,99,2\n'
        payload = gzip.compress(header + row*20000, mtime=0)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = root/'group.csv.gz'
            raw.write_bytes(payload)
            module = api()
            original = module.iter_updates

            def stop_on_large_group(lines, *, day, counts):
                def memory():
                    return 3*1024**3 if counts.rows >= 16000 else 0
                with patch.object(module, '_rss', side_effect=memory):
                    yield from original(lines, day=day, counts=counts)

            with patch.object(module, 'iter_updates', side_effect=stop_on_large_group):
                receipt = module.run_day(raw, day='2023-01-01', output=root/'run', protocol_commit=FREEZE,
                                         expected_sha256=hashlib.sha256(payload).hexdigest())
            self.assertEqual(receipt['status'], 'FAILED')
            self.assertLessEqual(receipt['quote_counts']['rows'], 16384)
            self.assertFalse((root/'run/report.json').exists())

    def test_original_fixture_records_every_intent_and_reconciles_private_outputs(self):
        payload = gzip.compress(b'exchange,symbol,timestamp,local_timestamp,ask_amount,ask_price,bid_price,bid_amount\n', mtime=0)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, output = root/'fixture.csv.gz', root/'run'
            raw.write_bytes(payload)
            receipt = api().run_day(raw, day='2023-01-01', output=output, protocol_commit=FREEZE,
                                    expected_sha256=hashlib.sha256(payload).hexdigest())
            self.assertEqual(receipt['status'], 'COMPLETE')
            report = json.loads((output/'report.json').read_text())
            self.assertEqual(report['scheduled_intents'], 86099)
            self.assertEqual(report['eligible_intents'], 0)
            with gzip.open(output/'audit.jsonl.gz', 'rt') as stream:
                self.assertEqual(sum(1 for _ in stream), 86099)
            for name, sha in receipt['artifacts_sha256'].items():
                self.assertEqual(hashlib.sha256((output/name).read_bytes()).hexdigest(), sha)
            with self.assertRaises(ValueError):
                api().run_day(raw, day='2023-01-01', output=output, protocol_commit=FREEZE,
                              expected_sha256=hashlib.sha256(payload).hexdigest())

    def test_later_stages_and_changed_raw_cannot_run_under_development_permission(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = root/'fixture.csv.gz'
            raw.write_bytes(b'wrong synthetic bytes')
            with self.assertRaises(ValueError):
                api().run_day(raw, day='2024-01-01', output=root/'later', protocol_commit=FREEZE,
                              expected_sha256='0'*64)
            receipt = api().run_day(raw, day='2023-01-01', output=root/'changed', protocol_commit=FREEZE,
                                    expected_sha256='0'*64)
            self.assertEqual(receipt['status'], 'FAILED')
            self.assertFalse((root/'changed/report.json').exists())


if __name__ == '__main__':
    unittest.main()
