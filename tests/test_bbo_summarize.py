"""Offline summarization fixtures; no provider rows or real private run access."""
import gzip
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


def api():
    try:
        module = importlib.import_module('scripts.bbo_summarize')
    except ModuleNotFoundError:
        module = None
    assert module is not None, 'offline BBO stage summarizer is not implemented'
    return module


def dump(path,payload):
    path.write_text(json.dumps(payload,sort_keys=True,indent=2)+'\n',encoding='utf-8')


def fixture(base):
    """Metadata-only synthetic zero-eligibility day, never replay evidence.

    The deliberately tiny audit is a hash fixture, not an independently verified
    86,099-row replay. The loader checks declared audit count, not provider history.
    """
    module=api()
    run=base/'2023-01-01-v1'
    run.mkdir()
    report=dict(day='2023-01-01',scheduled_intents=86099,eligible_intents=0,shock_intents=0,
                normal_intents=0,eligible_fraction=0.,exclusions={'SYNTHETIC_UNKNOWN':86099},
                side_counts=dict(scheduled=86099,buy_scheduled=43050,sell_scheduled=43049,
                                 buy_eligible=0,sell_eligible=0),groups={})
    dump(run/'report.json',report)
    (run/'savings.json.gz').write_bytes(gzip.compress(b'{}\n',mtime=0))
    (run/'audit.jsonl.gz').write_bytes(gzip.compress(b'original synthetic hash fixture; not a replay\n',mtime=0))
    (run/'method-source').mkdir()
    methods={}
    for name in module.CORE_FILES:
        payload=(module.ROOT/name).read_bytes()
        (run/'method-source'/Path(name).name).write_bytes(payload)
        methods[name]=hashlib.sha256(payload).hexdigest()
    methods['src/srl/bbo_runner.py']='0'*64  # Operational edits do not redefine scientific identity.
    artifacts={p.relative_to(run).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
               for p in run.rglob('*') if p.is_file()}
    receipt=dict(status='COMPLETE',protocol_commit=module.PROTOCOL_COMMIT,
                 audit_rows=86099,gzip_crc_verified=True,raw_sha256='1'*64,
                 expected_sha256='1'*64,raw_bytes=42,method_sha256=methods,
                 source_url='https://datasets.tardis.dev/v1/binance/book_ticker/2023/01/01/BTCUSDT.csv.gz',
                 artifacts_sha256=artifacts)
    dump(run/'receipt.json',receipt)
    return run,receipt


class ImportContractTests(unittest.TestCase):
    def test_loader_exists(self):
        self.assertTrue(callable(api().load_stage))


class SummarizerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.module=api()
        except AssertionError:
            raise unittest.SkipTest('import contract supplies implementation failure')

    def test_empty_external_stage_retains_twelve_missing_days(self):
        with tempfile.TemporaryDirectory() as folder:
            result=self.module.load_stage(Path(folder),'development')
            self.assertEqual(result['protocol_commit'],'76c8952ac6a18b6ab167878974f9cf2b4bad89c9')
            self.assertEqual(len(result['report']['days']),12)
            self.assertTrue(all(row['reason']=='MISSING_REPORT' for row in result['report']['days']))
            self.assertEqual(result['day_sources'],{})
            self.assertEqual(result['report']['status'],'DESCRIPTIVE_DEVELOPMENT')
            self.assertEqual(set(result['calculation_method_sha256']),set(self.module.CORE_FILES))
            self.assertNotIn(folder,json.dumps(result))

    def test_complete_coarse_metadata_and_current_scientific_hashes_are_bound(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder)
            _,receipt=fixture(base)
            result=self.module.load_stage(base,'development')
            self.assertEqual(result['day_sources']['2023-01-01'],dict(raw_sha256='1'*64,
                             compressed_bytes=42,source_url=receipt['source_url']))
            self.assertEqual(result['report']['days'][0]['status'],'COMPLETE')
            self.assertEqual(result['report']['primary']['paired_intents'],0)
            self.assertNotIn('src/srl/bbo_runner.py',result['calculation_method_sha256'])
            self.assertEqual(result['aggregation_method_sha256'],{
                'src/srl/bbo_report.py':hashlib.sha256((self.module.ROOT/'src/srl/bbo_report.py').read_bytes()).hexdigest()})

    def test_present_incomplete_or_unreceipted_run_stops_entire_stage(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder)
            run,receipt=fixture(base)
            for status in ('RUNNING','FAILED','INTERRUPTED'):
                receipt['status']=status
                dump(run/'receipt.json',receipt)
                with self.assertRaises(ValueError):self.module.load_stage(base,'development')
            (run/'receipt.json').unlink()
            with self.assertRaises(ValueError):self.module.load_stage(base,'development')

    def test_any_changed_missing_or_unlisted_artifact_fails_without_salvage(self):
        for change in ('changed','missing','unlisted'):
            with self.subTest(change=change),tempfile.TemporaryDirectory() as folder:
                base=Path(folder)
                run,_=fixture(base)
                if change=='changed':(run/'report.json').write_bytes(b'changed fixture')
                if change=='missing':(run/'audit.jsonl.gz').unlink()
                if change=='unlisted':(run/'unlisted.txt').write_bytes(b'synthetic')
                with self.assertRaises(ValueError):self.module.load_stage(base,'development')

    def test_identity_schedule_crc_and_core_hash_fail_closed(self):
        for change in ('url','digest','protocol','schedule','audit','crc','method'):
            with self.subTest(change=change),tempfile.TemporaryDirectory() as folder:
                base=Path(folder)
                run,receipt=fixture(base)
                if change=='url':receipt['source_url']='https://example.invalid/replacement'
                if change=='digest':receipt['raw_sha256']='A'*64
                if change=='protocol':receipt['protocol_commit']='0'*40
                if change=='audit':receipt['audit_rows']=1
                if change=='crc':receipt['gzip_crc_verified']=1
                if change=='method':receipt['method_sha256'][self.module.CORE_FILES[0]]='0'*64
                if change=='schedule':
                    report=json.loads((run/'report.json').read_text())
                    report['scheduled_intents']=1
                    dump(run/'report.json',report)
                    receipt['artifacts_sha256']['report.json']=hashlib.sha256((run/'report.json').read_bytes()).hexdigest()
                dump(run/'receipt.json',receipt)
                with self.assertRaises(ValueError):self.module.load_stage(base,'development')

    def test_traversal_links_and_in_repo_cache_are_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder)
            run,receipt=fixture(base)
            receipt['artifacts_sha256']['../escape']='0'*64
            dump(run/'receipt.json',receipt)
            with self.assertRaises(ValueError):self.module.load_stage(base,'development')
        with self.assertRaises(ValueError):self.module.load_stage(self.module.ROOT/'build','development')
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder)
            run,receipt=fixture(base)
            target=run/'audit.jsonl.gz'
            target.unlink()
            try:target.symlink_to(run/'savings.json.gz')
            except OSError:return
            with self.assertRaises(ValueError):self.module.load_stage(base,'development')

    def test_corrupt_gzip_and_duplicate_json_are_not_accepted_despite_matching_artifact_hash(self):
        for payload in (b'bad gzip',gzip.compress(b'{"shock/550":[],"shock/550":[]}',mtime=0)):
            with tempfile.TemporaryDirectory() as folder:
                base=Path(folder)
                run,receipt=fixture(base)
                path=run/'savings.json.gz'
                path.write_bytes(payload)
                receipt['artifacts_sha256']['savings.json.gz']=hashlib.sha256(payload).hexdigest()
                dump(run/'receipt.json',receipt)
                with self.assertRaises(ValueError):self.module.load_stage(base,'development')

    def test_changed_private_artifact_during_aggregation_cannot_return_success(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder)
            run,_=fixture(base)
            original=self.module.aggregate_stage
            def changed(*args,**kwargs):
                result=original(*args,**kwargs)
                (run/'audit.jsonl.gz').write_bytes(b'changed while calculating')
                return result
            with patch.object(self.module,'aggregate_stage',side_effect=changed),self.assertRaises(ValueError):
                self.module.load_stage(base,'development')
    def test_cli_exact_check_new_external_output_and_safe_summary(self):
        script=self.module.ROOT/'scripts/bbo_summarize.py'
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder)
            runs=base/'runs'
            runs.mkdir()
            output=base/'stage.json'
            command=[sys.executable,str(script),'--runs',str(runs),'--stage','development']
            first=subprocess.run(command+['--output',str(output)],capture_output=True,text=True,timeout=30)
            self.assertEqual(first.returncode,0,first.stdout)
            self.assertEqual(json.loads(first.stdout)['status'],'PASS')
            self.assertNotIn(folder,first.stdout)
            self.assertNotIn('day_sources',first.stdout)
            check=subprocess.run(command+['--check',str(output)],capture_output=True,text=True,timeout=30)
            self.assertEqual(check.returncode,0,check.stdout)
            original=output.read_bytes()
            output.write_bytes(b'preserve existing user work')
            repeat=subprocess.run(command+['--output',str(output)],capture_output=True,text=True,timeout=30)
            self.assertNotEqual(repeat.returncode,0)
            self.assertNotIn(folder,repeat.stdout+repeat.stderr)
            self.assertEqual(output.read_bytes(),b'preserve existing user work')
            output.write_bytes(original.replace(b'DESCRIPTIVE_DEVELOPMENT',b'CHANGED_DEVELOPMENT'))
            mismatch=subprocess.run(command+['--check',str(output)],capture_output=True,text=True,timeout=30)
            self.assertNotEqual(mismatch.returncode,0)
            self.assertNotIn(folder,mismatch.stdout+mismatch.stderr)


if __name__=='__main__':unittest.main()
