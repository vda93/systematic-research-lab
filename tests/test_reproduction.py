"""The figure and checked artifacts must follow calculations, not fixed captions."""

from copy import deepcopy
import json
import tempfile
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

from srl.visuals import render_summary
from scripts.reproduce import artifact_bytes, check_artifacts, write_output


ROOT = Path(__file__).resolve().parents[1]


class ReproductionTests(unittest.TestCase):
    def fixture(self):
        return {'main': {'control': {'net_total': -1.}, 'treatment': {'net_total': 2.},
                         'concentration': {'retained_total': -3., 'removed_cohorts': ['2040-01-01']},
                         'stop_rule': {'decision': 'REJECT'}},
                'calibration': {'nominal_coverage': .95, 'design': {'trials': 10},
                                'by_block': [{'block_size': 1, 'coverage': .5, 'monte_carlo_se': .158},
                                             {'block_size': 8, 'coverage': .8, 'monte_carlo_se': .126}]}}

    def test_accessible_svg_uses_reported_cohorts_and_decision(self):
        result = self.fixture()
        figure = render_summary(result)
        ET.fromstring(figure)
        self.assertIn('SYNTHETIC', figure)
        self.assertIn('Remove 1 cohort', figure)
        self.assertIn('REJECT', figure)
        result['main']['concentration'].update(retained_total=2., removed_cohorts=[])
        result['main']['stop_rule']['decision'] = 'PASS'
        changed = render_summary(result)
        self.assertIn('Remove 0 cohorts', changed)
        self.assertIn('PASS', changed)
        self.assertNotIn('REJECT', changed)

    def test_svg_covers_every_declared_calibration_block(self):
        figure = render_summary(self.fixture())
        self.assertIn('Block 1', figure)
        self.assertIn('Block 8', figure)
        self.assertIn('50.0%', figure)
        self.assertIn('80.0%', figure)
        self.assertIn('Nominal 95%', figure)

    def test_miniature_artifacts_replay_and_tamper_is_detected(self):
        protocol = json.loads((ROOT / 'experiments/protocol.json').read_text())
        protocol['inference']['repetitions'] = 19
        protocol['calibration'].update(trials=2, days=32, burn_in=16, repetitions=19)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'experiments').mkdir()
            (root / 'experiments/protocol.json').write_text(json.dumps(protocol))
            first = artifact_bytes(root)
            self.assertEqual(first, artifact_bytes(root))
            for name, data in first.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            self.assertEqual(check_artifacts(root, first), [])
            (root / 'results/study.json').write_text('changed')
            self.assertIn('results/study.json', check_artifacts(root, first))

    def test_output_never_overwrites_existing_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'new'
            receipt = write_output(target, {'result.json': b'{"synthetic":true}\n'}, {})
            self.assertEqual(len(receipt['artifacts']['result.json']), 64)
            with self.assertRaises(ValueError):
                write_output(target, {'result.json': b'changed'}, {})


if __name__ == '__main__':
    unittest.main()
