"""Public aggregate figure checks; no private strategy replay."""
from pathlib import Path
import importlib.util
import json
import re
import unittest
from copy import deepcopy
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

def renderer():
    path = ROOT / "scripts/render_macro.py"
    assert path.is_file(), "Macro aggregate renderer has not been implemented"
    spec = importlib.util.spec_from_file_location("render_macro", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def dataset():
    path = ROOT / "data/macro-public.json"
    assert path.is_file(), "Reviewed public Macro aggregate extract is missing"
    return json.loads(path.read_text(encoding="utf-8"))

class MacroFigureTests(unittest.TestCase):
    def test_mechanics_schematic_is_explicitly_nonempirical(self):
        figures=renderer().build_figures(dataset())
        assert 'macro-mechanics.svg' in figures
        text=figures['macro-mechanics.svg'].decode('utf-8')
        for label in ['CONCEPTUAL_SCHEMATIC','Fictional state example','Ask-based','Bid-based','Scheduled','Opposite pending']:
            assert label in text
        assert dataset()['mechanics']['historical_price_path'] is False
        assert dataset()['mechanics']['observed_latency'] is False
    def test_renderer_rejects_ambiguous_or_invalid_inputs(self):
        r = renderer()
        probes = []
        d = dataset(); d['baseline']['cells'].append(deepcopy(d['baseline']['cells'][0])); probes.append(d)
        d = dataset(); d['baseline']['cells'].pop(); probes.append(d)
        d = dataset(); d['baseline']['cells'][0]['spread_only_usd'] = float('nan'); probes.append(d)
        d = dataset(); d['baseline']['spread_only_usd'] += 1; probes.append(d)
        d = dataset(); d['calendar']['monthly'][0]['medium'] += 1; probes.append(d)
        d = dataset(); d['calendar']['monthly'][0]['medium'] += 1; d['calendar']['monthly'][0]['all'] += 1; probes.append(d)
        d = dataset(); d['calendar']['forensic_scope']['earlier_rate_as_reported'] += 1; probes.append(d)
        d = dataset(); d['calendar']['monthly'].pop(); probes.append(d)
        d = dataset(); d['calendar']['monthly'][1]['month'] = d['calendar']['monthly'][0]['month']; probes.append(d)
        d = dataset(); d['medium']['years'][0]['adjusted_usd'] += 1; probes.append(d)
        d = dataset(); d['medium']['pairs'].append(deepcopy(d['medium']['pairs'][0])); probes.append(d)
        d = dataset(); d['spread_filter']['pairs'][0]['delta_usd'] += 1; probes.append(d)
        d = dataset(); d['sequential']['combined_usd'] += 1; probes.append(d)
        for i, d in enumerate(probes):
            with self.subTest(probe=i), self.assertRaises(ValueError):
                r.build_figures(d)

    def test_consistent_baseline_change_updates_cells_and_summary_labels(self):
        r = renderer(); d = dataset(); original = r.build_figures(d)['macro-baseline.svg']
        row = d['baseline']['cells'][2]
        assert row['symbol'] == 'AUDUSD2' and row['year'] == 2023
        row['spread_only_usd'] += 10; row['gross_profit_usd'] += 10; row['trades'] += 1
        row['pf_as_reported'] = round(row['gross_profit_usd']/row['gross_loss_usd'], 6)
        d['baseline']['spread_only_usd'] += 10; d['baseline']['trades'] += 1
        d['baseline']['aggregate_pf_as_reported'] = round(sum(x['gross_profit_usd'] for x in d['baseline']['cells'])/sum(x['gross_loss_usd'] for x in d['baseline']['cells']), 4)
        changed = r.build_figures(d)['macro-baseline.svg']
        assert b'$546.00' in changed and b'+$4,260.48' in changed and b'1,397 recorded trades' in changed
        # The source cell's color mark changes as well as the numeric text.
        fills = lambda b: re.findall(rb'fill: (#[0-9a-f]+)', b)
        assert fills(original) != fills(changed)

    def test_consistent_calendar_change_updates_line_and_rate_annotations(self):
        r=renderer(); d=dataset(); original=r.build_figures(d)['macro-calendar.svg']
        d['calendar']['monthly'][0]['medium'] += 60
        d['calendar']['monthly'][0]['all'] += 60
        scope=d['calendar']['forensic_scope']; scope['earlier_rows'] += 60
        scope['earlier_rate_as_reported'] = round(scope['earlier_rows']/scope['earlier_months'],2)
        changed=r.build_figures(d)['macro-calendar.svg']
        assert b'16,348 rows' in changed and b'272.47' in changed
        paths=lambda b: re.findall(rb'<path d="([^"]+)"',b)
        assert paths(original) != paths(changed)

    def test_svg_accessibility_and_full_resolution_article_links(self):
        article = (ROOT/'studies/news-research.md').read_text(encoding='utf-8')
        assert 'â' not in article
        for name,content in renderer().build_figures(dataset()).items():
            root=ET.fromstring(content); ns={'s':'http://www.w3.org/2000/svg'}
            assert root.get('role') == 'img'
            assert root.get('aria-labelledby') == 'macro-title macro-desc'
            assert root.find('s:title',ns).get('id') == 'macro-title'
            assert root.find('s:desc',ns).get('id') == 'macro-desc'
            assert f'[Open full-resolution SVG](../figures/{name})' in article

    def test_original_baseline_matrix_reconciles(self):
        d = dataset()["baseline"]
        assert len(d["cells"]) == 10
        assert sum(c["trades"] for c in d["cells"]) == 1396
        assert round(sum(c["spread_only_usd"] for c in d["cells"]), 2) == 4250.48
        assert all(c["spread_only_usd"] > 0 for c in d["cells"])
        assert round(sum(c["gross_profit_usd"] for c in d["cells"]) / sum(c["gross_loss_usd"] for c in d["cells"]), 4) == 3.6889
        assert {(c["year"], c["symbol"]) for c in d["cells"]} == {(y,s) for y in [2023,2024] for s in ["AUDUSD2","EURUSD2","GBPUSD2","USDCAD2","USDJPY2"]}

    def test_cost_and_filter_accounting_keep_different_samples_separate(self):
        d = dataset()
        assert round(d["spread_filter"]["treatment_usd"]-d["spread_filter"]["control_usd"],2) == -7.62
        assert d["spread_filter"]["removed_completed_trades"] == 3
        for row in d["medium"]["years"]:
            assert round(row["spread_only_usd"] - row["commission_usd"],2) == row["adjusted_usd"]
        four = [r for r in d["medium"]["years"] if r["universe"] == "FOUR_PAIR_EXCLUDE_USDCAD2"]
        assert next(r for r in four if r["year"] == 2021)["adjusted_usd"] == -16.29
        assert round(sum(r["adjusted_usd"] for r in four),2) == 639.68
        for total in d["medium"]["totals"]:
            years = [r for r in d["medium"]["years"] if r["universe"] == total["universe"]]
            assert sum(r["trades"] for r in years) == total["trades"]
            for key in ["spread_only_usd", "commission_usd", "adjusted_usd"]:
                assert round(sum(r[key] for r in years), 2) == total[key]
        assert d["medium"]["cost_validation"] == "DOCUMENTATION_ONLY"

    def test_coverage_reconciles_to_original_forensic_scope(self):
        c = dataset()["calendar"]
        assert len(c["monthly"]) == 78
        assert sum(r["medium"] for r in c["monthly"] if r["month"] < "2025") == 16288
        assert sum(r["medium"] for r in c["monthly"] if r["month"] >= "2025") == 760
        assert c["earlier_scope"]["reported_total"] == 16059
        assert c["scope_reconciled"] is False
        assert c["later_result_classification"] == "INVALID_DATA_UNIVERSE"
        assert all(r["high"] + r["medium"] + r["low"] + r["unclassified"] == r["all"] for r in c["monthly"])

    def test_source_identity_and_no_private_locations(self):
        d = dataset()
        text = json.dumps(d)
        assert not re.search(r"[A-Z]:[\\/]|drive\.google|docs\.google|notion\.com|account_id|password|token", text, re.I)
        for s in d["sources"]:
            assert re.fullmatch(r"[a-f0-9]{64}",s["sha256"])
            assert "/" not in s["basename"] and "\\" not in s["basename"]
            assert s["publication_permission"] == "PUBLIC_AGGREGATE_ONLY"
            for member in s["members"]:
                assert re.fullmatch(r"[a-f0-9]{64}", member["sha256"])
        assert dataset()["sequential"]["independent_equity_paths"] is False

    def test_renderer_deterministic_and_canonical_svg(self):
        r=renderer(); d=dataset()
        a=r.build_figures(d); b=r.build_figures(d)
        assert a == b
        assert len(a) == 6
        for name, content in a.items():
            assert name.startswith("macro-") and name.endswith(".svg")
            root=ET.fromstring(content)
            assert root.tag.endswith("svg")
            assert b"<image" not in content
            assert (ROOT/"figures"/name).read_bytes() == content
        labels=b" ".join(a.values()).decode()
        assert "Commission" in labels and "DOCUMENTATION_ONLY" in labels
        assert "INVALID_DATA_UNIVERSE" in labels
        assert "sequential" in labels and "139" in labels
        assert "Spread-only" in labels

if __name__ == "__main__":
    unittest.main()
