# Apache-2.0. Copyright 2026 Munim, Inc. Made by MV2 of Munim, Inc. with AI agents.
"""Tests for senegal_groundnut 0.1.0 on a hand-traced 5-row fixture (not the real data)."""
import json
import os
import tempfile
import unittest

import senegal_groundnut as sg

HEADER = ["interview__key", "consent", "aflx_heard", "bac_heard", "prod_consall__1", "aflatoxin",
          "plate1_eb", "plate2_eb", "avecout_eb", "cfug_eb", "log10cfug_eb",
          "plate1_coli", "plate2_coli", "avecout_coli", "cfug_coli", "log10cfug_coli",
          "plate1_mold", "plate2_mold", "avecout_mold", "cfug_mold", "log10cfug_mold", "dry__id"]
ROWS = [
    # AA: two rows (two drying methods), identical lab values
    '"AA-01-02-03"\t1\t1\t0\t0\t2.5\t10\t12\t11\t1100\t3.041393\t5\t7\t6\t600\t2.778151\t3\t3\t3\t300\t2.477121\t1',
    '"AA-01-02-03"\t1\t1\t0\t0\t2.5\t10\t12\t11\t1100\t3.041393\t5\t7\t6\t600\t2.778151\t3\t3\t3\t300\t2.477121\t2',
    # BB: censored aflatoxin, no Enterobacteriaceae (log missing), no mould result
    '"BB-04-05-06"\t1\t0\t1\t1\t100\t0\t0\t0\t0\t\t1\t0\t0.5\t50\t1.69897\t\t\t\t\t\t1',
    # CC: aflatoxin exactly 4, coliforms 0 with log 0, mould log wrong (2.5 instead of 2.0)
    '"CC-07-08-09"\t1\t0\t0\t\t4.0\t2\t2\t2\t200\t2.30103\t0\t0\t0\t0\t0\t1\t1\t1\t100\t2.5\t1',
    # DD: refused
    '"DD-10-11-12"\t0\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t',
]
TEXT = "\t".join('"%s"' % h for h in HEADER) + "\n" + "\n".join(ROWS) + "\n"


class Parse(unittest.TestCase):
    def test_parse(self):
        rows = sg.parse_tab(TEXT)
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[0]["interview__key"], "AA-01-02-03")
        self.assertEqual(rows[2]["aflatoxin"], 100.0)
        self.assertIsNone(rows[2]["log10cfug_eb"])
        self.assertIsNone(rows[4]["dry__id"])

    def test_cell_and_round(self):
        self.assertIsNone(sg.cell_value("NaN"))
        self.assertEqual(sg.cell_value('"x y"'), "x y")
        self.assertTrue(sg.rounds_to(94.49, "94.5"))
        self.assertFalse(sg.rounds_to(94.44, "94.5"))
        self.assertTrue(sg.rounds_to(7.4, "7"))
        self.assertFalse(sg.rounds_to(None, "7"))

    def test_share(self):
        self.assertEqual(sg.share([1.0, 0.0, -999.0, None], lambda v: v == 1.0), (50.0, 2))
        self.assertEqual(sg.share([None], lambda v: True), (None, 0))


class Compute(unittest.TestCase):
    def setUp(self):
        self.c = sg.compute(sg.parse_tab(TEXT))

    def test_households(self):
        c = self.c
        self.assertEqual((c["n_rows"], c["n_households"], c["rows_per_household_max"]), (5, 4, 2))
        self.assertEqual(c["n_consent1"], 3)
        self.assertEqual(sum(c["lab_conflicts"].values()), 0)

    def test_survey_shares(self):
        c = self.c
        self.assertAlmostEqual(c["pct_aflx_heard"], 100.0 / 3, places=4)
        self.assertEqual(c["n_aflx_heard"], 3)
        self.assertAlmostEqual(c["pct_bac_heard"], 100.0 / 3, places=4)
        self.assertAlmostEqual(c["pct_prod_consall__1"], 50.0, places=4)
        self.assertAlmostEqual(c["pct_all_households_prod_consall__1"], 25.0, places=4)

    def test_aflatoxin(self):
        c = self.c
        self.assertEqual(c["n_aflatoxin"], 3)
        self.assertAlmostEqual(c["pct_afla_lt4"], 100.0 / 3, places=4)
        self.assertAlmostEqual(c["pct_afla_le4"], 200.0 / 3, places=4)
        self.assertAlmostEqual(c["pct_afla_ge100"], 100.0 / 3, places=4)
        self.assertAlmostEqual(c["pct_afla_gt100"], 0.0, places=4)
        self.assertEqual((c["afla_min"], c["afla_max"], c["afla_median"]), (2.5, 100.0, 4.0))
        self.assertEqual(c["afla_out_of_range_rows"], 0)

    def test_microbes(self):
        c = self.c
        self.assertEqual(c["n_log_eb"], 2)
        self.assertAlmostEqual(c["pct_log_gt1_eb"], 100.0, places=4)
        self.assertAlmostEqual(c["pct_cfug_gt10_eb"], 200.0 / 3, places=4)
        self.assertEqual(c["log_values_when_cfug_zero_eb"], ["missing"])
        self.assertEqual(c["n_log_coli"], 3)
        self.assertAlmostEqual(c["pct_log_gt1_coli"], 200.0 / 3, places=4)
        self.assertEqual(c["log_values_when_cfug_zero_coli"], [0.0])
        self.assertEqual((c["log_checked_eb"], c["log_mismatched_eb"]), (3, 0))
        self.assertEqual((c["log_checked_coli"], c["log_mismatched_coli"]), (3, 0))
        self.assertEqual((c["log_checked_mold"], c["log_mismatched_mold"]), (3, 1))
        self.assertEqual((c["avg_checked_eb"], c["avg_mismatched_eb"]), (4, 0))
        self.assertEqual((c["avg_checked_coli"], c["avg_mismatched_coli"]), (4, 0))
        self.assertEqual((c["avg_checked_mold"], c["avg_mismatched_mold"]), (3, 0))
        self.assertEqual(c["cfug_per_average_count_eb"], [100.0])

    def test_conflict(self):
        c = sg.compute([{"interview__key": "X", "aflatoxin": 1.0}, {"interview__key": "X", "aflatoxin": 2.0}])
        self.assertEqual(c["lab_conflicts"]["aflatoxin"], 1)
        self.assertEqual(c["n_households"], 1)
        self.assertEqual(c["afla_min"], 1.0)


class Checks(unittest.TestCase):
    def setUp(self):
        self.results = sg.checks(sg.compute(sg.parse_tab(TEXT)))
        self.by_id = {r["id"]: r for r in self.results}

    def test_ids(self):
        self.assertEqual([r["id"] for r in self.results], ["S%d" % i for i in range(1, 13)])

    def test_selected(self):
        b = self.by_id
        self.assertEqual(b["S1"]["computed"], [4, 3])
        self.assertFalse(b["S1"]["held"])
        self.assertFalse(b["S7"]["held"])
        self.assertTrue(b["S9"]["held"])
        self.assertEqual(b["S10"]["computed"], [1, 9])
        self.assertFalse(b["S10"]["held"])
        self.assertEqual(b["S11"]["computed"], [0, 11])
        self.assertTrue(b["S11"]["held"])
        self.assertTrue(b["S12"]["held"])

    def test_predictions(self):
        p = sg.predictions(self.results)
        self.assertEqual(p["n_held"], 3)
        self.assertFalse(p["P1 S1 holds"])
        self.assertFalse(p["P2 at least 9 of 12 checks hold"])
        self.assertFalse(p["P3 S9-S12 all hold"])
        self.assertTrue(p["P4 (guess) at least one of S4-S7 fails"])
        self.assertEqual(p["n_checks"], 12)


class Main(unittest.TestCase):
    def test_main_writes_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "fixture.tab")
            with open(src, "w", encoding="utf-8") as fh:
                fh.write(TEXT)
            out = os.path.join(tmp, "out")
            self.assertEqual(sg.main(["--out-dir", out, "--tab-file", src]), 0)
            with open(os.path.join(out, "senegal_groundnut_check.json"), encoding="utf-8") as fh:
                report = json.load(fh)
            self.assertEqual(report["version"], "0.1.0")
            self.assertEqual(len(report["checks"]), 12)
            self.assertEqual(report["stats"]["n_households"], 4)


if __name__ == "__main__":
    unittest.main()
