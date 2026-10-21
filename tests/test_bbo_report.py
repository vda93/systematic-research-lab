"""Original hand-constructed stage summaries; no market observations."""
import copy
import importlib
import json
import statistics
import unittest


def api():
    try:
        module = importlib.import_module('srl.bbo_report')
    except ModuleNotFoundError:
        module = None
    assert module is not None, 'all-planned-day BBO reporting is not implemented'
    return module


def days(year=2025):
    return [f'{year}-{month:02d}-01' for month in range(1, 13)]


def summary(values):
    ordered = sorted(values)
    penalty = sorted(-x for x in values)
    return dict(count=len(values), mean=statistics.mean(values) if values else None,
                sample_sd=statistics.stdev(values) if len(values)>1 else None,
                median_saving=ordered[(len(ordered)-1)//2] if ordered else None,
                penalty_quantiles={str(p): penalty[(p*len(values)+99)//100-1] if values else None
                                   for p in (50, 90, 95, 99)},
                worst_penalty=penalty[-1] if penalty else None)


def group(values, *, eligible=None, missing=0, bad_depth=0, slope=0.):
    n = len(values)
    eligible = n+missing if eligible is None else eligible
    mean = statistics.mean(values) if values else None
    price = mean+.5-5*slope if mean is not None else None
    components = {name: None for name in ('price_saving', 'spread_saving', 'mid_drift_saving', 'fee_slope')}
    if n:
        components = dict(price_saving=price, spread_saving=price-.5, mid_drift_saving=.5, fee_slope=slope)
    return dict(summary(values), eligible=eligible, paired=n, mean_saving_bps=mean,
                missing_baseline=missing, missing_delayed=missing, both_missing=missing,
                baseline_depth_fail=bad_depth, delayed_depth_fail=0, either_depth_fail=bad_depth,
                sufficient_depth_both=n-bad_depth, mean_components=components,
                mean_cost_grid_bps={f'{fee:g}/{slip:g}': price+fee*slope-slip if n else None
                                    for fee in (0.,5.,10.) for slip in (0.,.5,1.)},
                post_outcome_depth_subset=summary(values[bad_depth:]))


def fixture(mean=.5, n=100, *, missing=0, coverage=1., bad_depth=0, slope=0.):
    scheduled = round((n+missing)/coverage)
    eligible = n+missing
    left = eligible//2
    missing_buy = min(missing, left)
    missing_sell = missing-missing_buy
    buy = [mean]*(left-missing_buy)
    sell = [mean]*(eligible-left-missing_sell)
    pooled = buy+sell
    samples, groups = {}, {}
    for delay in (300,550,1050):
        for suffix, values, missing_n, bad in [('',pooled,missing,bad_depth),
                                            ('/buy',buy,missing_buy,bad_depth),
                                            ('/sell',sell,missing_sell,0)]:
            key = f'shock/{delay}{suffix}'
            samples[key] = values
            groups[key] = group(values, missing=missing_n, bad_depth=bad, slope=slope)
    report = dict(scheduled_intents=scheduled, eligible_intents=eligible,
                  shock_intents=eligible, normal_intents=0,
                  eligible_fraction=eligible/scheduled,
                  exclusions={'SYNTHETIC_EXCLUSION':scheduled-eligible} if scheduled>eligible else {},
                  side_counts=dict(scheduled=scheduled,buy_scheduled=scheduled//2,
                                   sell_scheduled=scheduled-scheduled//2,
                                   buy_eligible=left,sell_eligible=eligible-left),
                  groups=groups)
    return report, samples


def stage_fixture(means, *, year=2025, **kwargs):
    reports, samples = {}, {}
    for day, mean in zip(days(year), means):
        reports[day], samples[day] = fixture(mean, **kwargs)
    return reports, samples


class ImportContractTests(unittest.TestCase):
    def test_api_exists(self):
        self.assertTrue(callable(api().aggregate_stage))


class StageTests(unittest.TestCase):
    def test_both_missing_quotes_cannot_contribute_a_displayed_depth_failure(self):
        report, samples = fixture(.5, n=20, missing=5)
        for values in report['groups'].values():
            # All paired quotes are declared sufficient; all remaining intents
            # lack BOTH quotes, so none can have an observed depth failure.
            values['baseline_depth_fail'] = values['both_missing']
            values['either_depth_fail'] = values['both_missing']
        with self.assertRaises(ValueError):
            self.module.aggregate_stage(days(2023), {days(2023)[0]: report},
                                        {days(2023)[0]: samples}, stage='development')

    @classmethod
    def setUpClass(cls):
        try:
            cls.module = api()
        except AssertionError:
            raise unittest.SkipTest('import contract supplies missing implementation failure')

    def aggregate(self, means, **kwargs):
        reports, samples = stage_fixture(means)
        return self.module.aggregate_stage(days(), reports, samples, stage='final',
                                           external_gates_passed=True, **kwargs)

    def test_favorable_final_has_all_days_nine_cells_and_no_private_samples(self):
        reports, samples = stage_fixture([.5]*10, slope=.01)
        reports[days()[0]]['private_event_prices'] = [123456.789]
        result = self.module.aggregate_stage(days(), reports, samples, stage='final',
                    missing_reasons={days()[10]:'SOURCE_UNAVAILABLE'}, external_gates_passed=True)
        self.assertEqual(result['status'], 'HISTORICAL_QUOTE_COST_SCREEN_PASS')
        self.assertEqual(len(result['days']), 12)
        self.assertEqual(result['days'][10]['reason'], 'SOURCE_UNAVAILABLE')
        self.assertEqual(result['days'][11]['reason'], 'MISSING_REPORT')
        self.assertEqual(result['primary']['inference']['mean'], .5)
        self.assertEqual(result['support']['days_with_100_shocks'], 10)
        self.assertEqual(len(result['groups']), 18)
        grid = result['primary']['mean_cost_grid_bps']
        self.assertEqual(len(grid), 9)
        self.assertAlmostEqual(grid['0/0'], .95)
        self.assertAlmostEqual(grid['5/0.5'], .5)
        self.assertAlmostEqual(result['primary']['mean_components']['fee_saving_bps'], .05)
        self.assertEqual(result['primary']['mean_components']['slippage_saving_bps'], -.5)
        self.assertNotIn('private_event_prices', json.dumps(result))
        self.assertNotIn('samples', result)
        self.assertNotIn('savings', result)
        self.assertIsNone(result['primary']['post_outcome_depth_subset']['pooled_penalty_quantiles'])

    def test_missing_and_low_n_fail_support_before_negative_or_positive_economics(self):
        for means in ([], [-.5]*2, [.5]*9):
            result = self.aggregate(means)
            self.assertEqual(result['status'], 'FAIL_SUPPORT')
            self.assertEqual(len(result['days']),12)
        result = self.aggregate([.5]*2)
        self.assertIsNone(result['primary']['inference']['ci95'])
        self.assertEqual(result['primary']['contributing_days'],2)

    def test_full_support_negative_zero_small_positive_and_external_gates(self):
        self.assertEqual(self.aggregate([-.5]*10)['status'], 'NEGATIVE')
        self.assertEqual(self.aggregate([0.]*10)['status'], 'NEGATIVE')
        self.assertEqual(self.aggregate([.05]*10)['status'], 'INCONCLUSIVE')
        reports,samples=stage_fixture([.5]*10)
        result=self.module.aggregate_stage(days(),reports,samples,stage='final')
        self.assertEqual(result['status'],'NOT_RUN_EXTERNAL_GATES')

    def test_coverage_depth_and_unpaired_eligible_day_cannot_be_dropped(self):
        for changed in (dict(coverage=.94),dict(bad_depth=2)):
            reports,samples=stage_fixture([.5]*10,**changed)
            result=self.module.aggregate_stage(days(),reports,samples,stage='final',external_gates_passed=True)
            self.assertEqual(result['status'],'FAIL_SUPPORT')
            self.assertEqual(result['primary']['contributing_days'],10)
        reports,samples=stage_fixture([.5]*10)
        reports[days()[10]],samples[days()[10]]=fixture(.5,n=0,missing=100)
        result=self.module.aggregate_stage(days(),reports,samples,stage='final',external_gates_passed=True)
        self.assertFalse(result['support']['zero_missing_primary_targets'])
        self.assertEqual(result['status'],'FAIL_SUPPORT')
        self.assertEqual(result['days'][10]['paired_shocks'],0)

    def test_low_shock_contributing_day_stays_in_estimate_and_depth_subset_is_descriptive(self):
        reports,samples=stage_fixture([.5]*10)
        reports[days()[10]],samples[days()[10]]=fixture(-10.,n=2)
        result=self.module.aggregate_stage(days(),reports,samples,stage='final',external_gates_passed=True)
        self.assertAlmostEqual(result['primary']['inference']['mean'],-5/11)
        self.assertEqual(result['primary']['contributing_days'],11)
        self.assertEqual(result['support']['days_with_100_shocks'],10)
        self.assertEqual(result['status'],'NEGATIVE')
        self.assertEqual(result['primary']['post_outcome_depth_subset']['contributing_days'],11)

    def test_leave_one_out_contradiction_limits_favorable_primary(self):
        result=self.aggregate([4.]+[.01]*9)
        self.assertGreater(result['primary']['inference']['ci95'][0],0)
        self.assertGreaterEqual(result['primary']['inference']['mean'],.1)
        self.assertEqual(result['status'],'SENSITIVITY_DEPENDENT')
        self.assertTrue(result['sensitivity_contradictions']['leave_one_day_out'])

    def test_equal_day_mean_and_tail_weights_are_not_pooled_intent_weights(self):
        reports,samples=stage_fixture([-10.],year=2023)
        reports[days(2023)[1]],samples[days(2023)[1]]=fixture(0.,n=900)
        result=self.module.aggregate_stage(days(2023),reports,samples,stage='development')
        self.assertEqual(result['status'],'DESCRIPTIVE_DEVELOPMENT')
        self.assertEqual(result['primary']['inference']['mean'],-5.)
        self.assertEqual(result['primary']['equal_day_penalty_quantiles']['quantiles'],
                         {'50':0.,'90':10.,'95':10.,'99':10.})
        self.assertEqual(result['primary']['worst_day']['day'],days(2023)[0])
        self.assertEqual(result['primary']['worst_observed_penalty'],10.)

    def test_completed_zero_eligibility_day_needs_no_private_vectors(self):
        report=dict(scheduled_intents=100,eligible_intents=0,shock_intents=0,normal_intents=0,
                    exclusions={'SYNTHETIC_MISSING':100},eligible_fraction=0.,groups={},
                    side_counts=dict(scheduled=100,buy_scheduled=50,sell_scheduled=50,buy_eligible=0,sell_eligible=0))
        result=self.module.aggregate_stage(days(2023),{days(2023)[0]:report},{},stage='development')
        self.assertEqual(result['status'],'DESCRIPTIVE_DEVELOPMENT')
        self.assertEqual(result['primary']['paired_intents'],0)
        self.assertIsNone(result['days'][0]['mean_saving_bps'])
        self.assertIsNone(result['primary']['inference']['ci95'])

    def test_block_two_contradiction_is_not_rescued_by_positive_leave_one_out(self):
        result=self.aggregate([-.25]*4+[1.]*6)
        self.assertGreater(result['primary']['inference']['ci95'][0],0)
        self.assertLessEqual(result['primary']['inference']['sensitivity_ci95'][0],0)
        self.assertFalse(result['sensitivity_contradictions']['leave_one_day_out'])
        self.assertTrue(result['sensitivity_contradictions']['block_two'])
        self.assertEqual(result['status'],'SENSITIVITY_DEPENDENT')

    def test_favorable_normal_and_latency_controls_cannot_rescue_negative_primary(self):
        reports,samples=stage_fixture([-.5]*10)
        for day in reports:
            normal_report,normal_samples=fixture(20.)
            for key,value in normal_report['groups'].items():
                reports[day]['groups'][key.replace('shock/','normal/')]=value
            for key,value in normal_samples.items():
                samples[day][key.replace('shock/','normal/')]=value
            reports[day].update(scheduled_intents=200,eligible_intents=200,normal_intents=100,
                               side_counts=dict(scheduled=200,buy_scheduled=100,sell_scheduled=100,buy_eligible=100,sell_eligible=100))
        result=self.module.aggregate_stage(days(),reports,samples,stage='final',external_gates_passed=True)
        self.assertEqual(result['status'],'NEGATIVE')
        self.assertEqual(result['groups']['normal/550']['equal_day_summary']['mean'],20.)
        self.assertEqual(result['groups']['shock/550/buy']['paired_intents'],500)
        self.assertEqual(result['groups']['shock/300']['mean_cost_grid_bps']['5/0.5'],-.5)
    def test_validation_is_descriptive_even_if_all_favorable(self):
        reports,samples=stage_fixture([.5]*12,year=2024)
        result=self.module.aggregate_stage(days(2024),reports,samples,stage='validation',external_gates_passed=True)
        self.assertEqual(result['status'],'DESCRIPTIVE_VALIDATION')

    def test_strict_counts_means_grid_components_and_finite_values_reconcile(self):
        for damage in ('count','mean','grid','component','private','side','depth'):
            reports,samples=stage_fixture([.5]*10)
            g=reports[days()[0]]['groups']['shock/550']
            if damage=='count':g['paired']+=1
            if damage=='mean':g['mean_saving_bps']=99
            if damage=='grid':g['mean_cost_grid_bps'].pop('0/0')
            if damage=='component':g['mean_components']['mid_drift_saving']=99
            if damage=='private':samples[days()[0]]['shock/550'][0]=float('nan')
            if damage=='side':reports[days()[0]]['side_counts']['buy_eligible']+=1
            if damage=='depth':g['sufficient_depth_both']=True
            with self.subTest(damage=damage),self.assertRaises(ValueError):
                self.module.aggregate_stage(days(),reports,samples,stage='final',external_gates_passed=True)

    def test_planned_identity_unknown_days_and_missing_samples_fail_closed(self):
        reports,samples=stage_fixture([.5]*10)
        for planned in (days()[:-1],list(reversed(days())),days(2024)):
            with self.assertRaises(ValueError):
                self.module.aggregate_stage(planned,reports,samples,stage='final')
        altered=copy.deepcopy(samples)
        del altered[days()[0]]['shock/550']
        with self.assertRaises(ValueError):
            self.module.aggregate_stage(days(),reports,altered,stage='final')
        reports['2026-01-01']=reports[days()[0]]
        with self.assertRaises(ValueError):
            self.module.aggregate_stage(days(),reports,samples,stage='final')


if __name__=='__main__':
    unittest.main()
