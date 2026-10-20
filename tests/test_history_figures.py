"""Historical figures must depend on curated source values and retain scope."""

from copy import deepcopy
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from scripts.render_historical import historical_artifacts


ROOT = Path(__file__).resolve().parents[1]


class HistoricalFigureTests(unittest.TestCase):
    def test_all_figures_rebuild_and_transcription_change_is_visible(self):
        data = json.loads((ROOT / 'data/historical-results.json').read_text())
        first = historical_artifacts(data)
        self.assertEqual(len(first), 5)
        self.assertEqual(first, historical_artifacts(data))
        for name, payload in first.items():
            if name.endswith('.svg'):
                ET.fromstring(payload)
                self.assertIn(b'Historical', payload)
        changed = deepcopy(data)
        changed['records'][0]['metrics']['long_total_r'] = -8.0
        other = historical_artifacts(changed)
        self.assertNotEqual(first['figures/momentum.svg'], other['figures/momentum.svg'])
        self.assertIn(b'-8.00', other['figures/momentum.svg'])

    def test_oos_sample_labels_follow_published_records(self):
        data=json.loads((ROOT/'data/historical-results.json').read_text())
        next(row for row in data['records'] if row['id']=='O2_A')['metrics']['trades']=999
        figure=historical_artifacts(data)['figures/orb.svg']
        self.assertIn(b'n=999',figure)
        self.assertNotIn(b'n=124',figure)

    def test_interval_can_exclude_point_estimate_without_negative_errorbars(self):
        data=json.loads((ROOT/'data/historical-results.json').read_text())
        next(row for row in data['records'] if row['id']=='N1')['metrics'].update(estimate=0.,ci_low=.1,ci_high=.3)
        figure=historical_artifacts(data)['figures/nowick.svg']
        ET.fromstring(figure)


if __name__ == '__main__':
    unittest.main()
