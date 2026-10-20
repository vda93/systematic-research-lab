"""Historical presentation cannot silently strengthen or corrupt source reports."""

from copy import deepcopy
import unittest

from srl.historical import validate_records, render_tables


class HistoricalTests(unittest.TestCase):
    def fixture(self):
        return {'scope': 'HISTORICAL_REPORTED_AGGREGATES', 'records': [
            {'id': 'EXAMPLE', 'program': 'Example', 'source_record': 'Completed report',
             'sample_type': 'development', 'period_start': '2020-01-01',
             'period_end_exclusive': '2021-01-01', 'limitations': 'Known sample, no fresh validation.',
             'metrics': {'trades': 10, 'total_r': 2.0, 'pf_r': 1.1}}]}

    def test_valid_record_and_report_include_scope_and_all_metrics(self):
        data = self.fixture()
        validate_records(data)
        table = render_tables(data)
        self.assertIn('EXAMPLE', table)
        self.assertIn('total_r', table)
        self.assertIn('2.0', table)
        self.assertIn('development', table)
        self.assertIn('Known sample', table)

    def test_nonfinite_boolean_metrics_duplicate_ids_and_unseen_labels_rejected(self):
        for value in (float('nan'), float('inf'), True):
            data = self.fixture()
            data['records'][0]['metrics']['total_r'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_records(data)
        data = self.fixture()
        data['records'] *= 2
        with self.assertRaises(ValueError):
            validate_records(data)
        data = self.fixture()
        data['records'][0]['sample_type'] = 'fresh_oos'
        with self.assertRaises(ValueError):
            validate_records(data)

    def test_dates_counts_and_missing_source_context_fail_closed(self):
        for field, value in [('source_record', ''), ('limitations', ''),
                             ('period_end_exclusive', '2019-01-01')]:
            data = self.fixture()
            data['records'][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_records(data)
        for count in (-1, 1.5, True):
            data = self.fixture()
            data['records'][0]['metrics']['trades'] = count
            with self.assertRaises(ValueError):
                validate_records(data)

    def test_interval_bounds_ordered_and_retained_metrics_can_be_negative(self):
        data = self.fixture()
        data['records'][0]['metrics'] = {'estimate': -.1, 'ci_low': -.3, 'ci_high': -.01}
        validate_records(data)
        bad = deepcopy(data)
        bad['records'][0]['metrics']['ci_high'] = -.4
        with self.assertRaises(ValueError):
            validate_records(bad)

    def test_prefixed_counts_probability_and_unsigned_units_have_domains(self):
        for key,value in [('long_trades',-1.5),('short_trades',1.2),
                          ('holm_adjusted_p',2),('after_max_actual_risk_pct',-5),
                          ('canonical_maxdd_r',-1),('candidate_a_pf_money',-.2)]:
            data=self.fixture()
            data['records'][0]['metrics'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                validate_records(data)

    def test_percentile_interval_need_not_contain_point_estimate(self):
        data=self.fixture()
        data['records'][0]['metrics']={'estimate':0.,'ci_low':.1,'ci_high':.3}
        validate_records(data)


if __name__ == '__main__':
    unittest.main()
