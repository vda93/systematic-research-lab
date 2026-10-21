"""Offline checked aggregate comparison with original synthetic JSON."""
import importlib
import json
from pathlib import Path
import tempfile
import unittest


class CheckedDayTests(unittest.TestCase):
    def test_changed_results_or_raw_identity_fail_closed(self):
        try:
            module = importlib.import_module('scripts.bbo_check_day')
        except ModuleNotFoundError:
            self.fail('offline aggregate comparison command is missing')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = root/'run'
            run.mkdir()
            report = {'day': '2023-01-01', 'scheduled_intents': 3, 'eligible_intents': 0}
            checked = {'raw_sha256': 'a'*64, 'method_sha256': {}, 'report': report}
            (root/'checked.json').write_text(json.dumps(checked))
            (run/'report.json').write_text(json.dumps(report))
            receipt = {'status': 'COMPLETE', 'raw_sha256': 'a'*64, 'method_sha256': {}}
            (run/'receipt.json').write_text(json.dumps(receipt))
            self.assertEqual(module.check_day(run, root/'checked.json'), [])
            report['eligible_intents'] = 1
            (run/'report.json').write_text(json.dumps(report))
            self.assertTrue(module.check_day(run, root/'checked.json'))
            (run/'report.json').write_text(json.dumps({'day': '2023-01-01', 'scheduled_intents': 3, 'eligible_intents': 0}))
            receipt['raw_sha256'] = 'b'*64
            (run/'receipt.json').write_text(json.dumps(receipt))
            self.assertTrue(module.check_day(run, root/'checked.json'))


if __name__ == '__main__':
    unittest.main()
