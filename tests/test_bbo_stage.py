"""Immutable local stage closeouts; original temporary Git repositories only."""
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


def api():
    try:
        return importlib.import_module('srl.bbo_stage')
    except ModuleNotFoundError:
        raise AssertionError('immutable BBO stage guard is missing') from None


class StageTests(unittest.TestCase):
    def test_later_stage_requires_frozen_usable_preceding_stage_and_exact_current_methods(self):
        module = api()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.run(['git', '-c', 'core.hooksPath=', '-C', str(root), *args], check=True,
                                      capture_output=True, text=True).stdout.strip()
            git('init', '-b', 'fixture')
            methods = {}
            for name in module.REQUIRED_FILES:
                path = root/name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'original synthetic implementation fixture\n')
                methods[name] = hashlib.sha256(path.read_bytes()).hexdigest()
            def commit():
                git('add', '.')
                git('-c', 'user.name=Synthetic fixture', '-c', 'user.email=fixture@example.invalid',
                    '-c', 'commit.gpgsign=false', 'commit', '-qm', 'fixture: freeze original synthetic inputs')
                return git('rev-parse', 'HEAD')
            implementation = commit()
            with self.assertRaises(ValueError):
                module.verify_stage(root, day='2024-01-01', implementation_commit=implementation,
                                    stage_commit=implementation)
            closeout = root/'data/bbo-development-closeout.json'
            closeout.parent.mkdir(exist_ok=True)
            record = dict(status='READY_FOR_VALIDATION', correctness_verified=True,
                          usable_price_paired_shocks=0, method_sha256=methods)
            closeout.write_text(json.dumps(record))
            zero = commit()
            with self.assertRaises(ValueError):
                module.verify_stage(root, day='2024-01-01', implementation_commit=implementation, stage_commit=zero)
            record['usable_price_paired_shocks'] = 1
            closeout.write_text(json.dumps(record))
            ready = commit()
            with self.assertRaises(ValueError):
                module.verify_stage(root, day='2024-01-01', implementation_commit=implementation,
                                    stage_commit=ready)
            protocol = '76c8952ac6a18b6ab167878974f9cf2b4bad89c9'
            def linked_result(stage, year):
                planned = [f'{year}-{month:02}-01' for month in range(1,13)]
                data = dict(protocol_commit=protocol, day_sources={day:dict(raw_sha256='a'*64,
                           source_url=f'https://datasets.tardis.dev/v1/binance/book_ticker/{day.replace("-", "/")}/BTCUSDT.csv.gz') for day in planned},
                            report=dict(stage=stage, days=[dict(day=day, status='COMPLETE', paired_shocks=1 if index==0 else 0)
                                                         for index,day in enumerate(planned)]))
                path = root/f'data/bbo-{stage}-results.json'
                path.write_text(json.dumps(data))
                return hashlib.sha256(path.read_bytes()).hexdigest()
            record.update(protocol_commit=protocol, results_sha256=linked_result('development',2023))
            closeout.write_text(json.dumps(record))
            ready = commit()
            result = module.verify_stage(root, day='2024-01-01', implementation_commit=implementation,
                                         stage_commit=ready)
            self.assertEqual(result['stage'], 'VALIDATION')
            with self.assertRaises(ValueError):
                module.verify_stage(root, day='2025-01-01', implementation_commit=implementation, stage_commit=ready)
            validation = root/'data/bbo-validation-closeout.json'
            validation.write_text(json.dumps(dict(status='READY_FOR_FINAL', correctness_verified=True,
                                                  method_sha256=methods,protocol_commit=protocol,
                                                  results_sha256=linked_result('validation',2024))))
            final = commit()
            self.assertEqual(module.verify_stage(root, day='2025-01-01', implementation_commit=implementation,
                                                 stage_commit=final)['stage'], 'FINAL')
            (root/module.REQUIRED_FILES[0]).write_bytes(b'changed synthetic code\n')
            with self.assertRaises(ValueError):
                module.verify_stage(root, day='2024-01-01', implementation_commit=implementation, stage_commit=ready)


if __name__ == '__main__':
    unittest.main()
