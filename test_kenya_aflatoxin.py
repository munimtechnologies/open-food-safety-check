# Apache-2.0. Copyright 2026 Munim, Inc. Made by MV2 of Munim, Inc. with AI agents.
"""Tests for kenya_aflatoxin 0.1.0 on a hand-traced 8-row fixture (not the real data)."""
import json
import os
import tempfile
import unittest

import kenya_aflatoxin as ka

HEADER = ["location_sample", "round", "brand_id", "is_posho", "result", "sample_cat", "detail_cat",
          "grade_cat", "is_over_10ppb", "location_mill"]
ROWS = [
    "2\t3\t7\t0\t12.0\t2\t2\t1\t1\t2",     # r1 Kajiado regional brand, June, over 10
    "2\t5\t7\t0\t4.0\t2\t2\t1\t0\t2",      # r2 Kajiado regional brand, October
    "10\t3\t9\t0\t2.0\t1\t1\t1\t0\t10",    # r3 Thika national brand, June
    "10\t6\t9\t0\t0.2\t1\t1\t1\t0\t10",    # r4 below the 0.5 ppb LOD, December
    "3\t3\t\t1\t20.0\t3\t3\t\t1\t3",       # r5 posho, purchased grain, June, no grade
    "3\t6\t\t1\t6.0\t3\t4\t2\t0\t3",       # r6 posho, home-grown grain, less refined
    "3\t5\t\t1\t8.0\t3\t3\t3\t1\t3",       # r7 posho, purchased, more refined; flag wrongly 1
    "1\t1\t\t1\t\t3\t3\t\t\t1",            # r8 no result: not an analysed sample
]
TEXT = "\t".join('"%s"' % h for h in HEADER) + "\n" + "\n".join(ROWS) + "\n"


class ParseAndRound(unittest.TestCase):
    def test_parse(self):
        rows = ka.parse_tab(TEXT)
        self.assertEqual(len(rows), 8)
        self.assertEqual(rows[0]["location_mill"], 2.0)
        self.assertIsNone(rows[4]["brand_id"])
        self.assertIsNone(rows[7]["result"])

    def test_rounds_to(self):
        self.assertTrue(ka.rounds_to(4.85, "4.9"))
        self.assertFalse(ka.rounds_to(4.84, "4.9"))
        self.assertTrue(ka.rounds_to(16.4, "16"))
        self.assertFalse(ka.rounds_to(16.5, "16"))
        self.assertTrue(ka.rounds_to(32.04, "32.0"))
        self.assertFalse(ka.rounds_to(None, "1"))


class Compute(unittest.TestCase):
    def setUp(self):
        self.c = ka.compute(ka.parse_tab(TEXT))

    def test_counts(self):
        c = self.c
        self.assertEqual((c["n_rows"], c["n_result_missing"], c["n_analysed"]), (8, 1, 7))
        self.assertEqual((c["n_branded"], c["n_posho"]), (4, 3))
        self.assertEqual(c["n_below_lod"], 1)
        self.assertEqual(c["flag_disagreements"], 1)
        self.assertEqual(c["flag_missing"], 0)

    def test_shares_and_means(self):
        c = self.c
        self.assertAlmostEqual(c["pct_detectable"], 600.0 / 7, places=4)
        self.assertAlmostEqual(c["pct_over_10"], 200.0 / 7, places=4)
        self.assertAlmostEqual(c["mean_branded"], 4.55, places=4)
        self.assertAlmostEqual(c["mean_posho"], 34.0 / 3, places=4)
        self.assertAlmostEqual(c["mean_national"], 1.1, places=4)
        self.assertAlmostEqual(c["mean_regional"], 8.0, places=4)
        self.assertAlmostEqual(c["mean_homegrown"], 6.0, places=4)
        self.assertAlmostEqual(c["mean_purchased"], 14.0, places=4)
        self.assertAlmostEqual(c["pct_over_branded"], 25.0, places=4)
        self.assertAlmostEqual(c["pct_over_regional"], 50.0, places=4)
        self.assertAlmostEqual(c["pct_over_posho"], 100.0 / 3, places=4)

    def test_table2(self):
        t = self.c["table2"]
        self.assertEqual(t[2], (2, 0, 2, 0, 0, 0))
        self.assertEqual(t[10], (2, 2, 0, 0, 0, 0))
        self.assertEqual(t[3], (0, 0, 0, 3, 2, 1))
        self.assertEqual(t[1], (0, 0, 0, 0, 0, 0))

    def test_brands_kajiado_late(self):
        c = self.c
        self.assertEqual(c["n_brands"], 2)
        self.assertAlmostEqual(c["brand_mean_min"], 1.1, places=4)
        self.assertAlmostEqual(c["brand_mean_max"], 8.0, places=4)
        self.assertIsNone(c["brand_mean_min_n3"])
        self.assertEqual((c["kajiado_branded_n"], c["kajiado_branded_n_over"]), (2, 1))
        self.assertEqual(c["kajiado_branded_brands"], [7])
        self.assertEqual(c["late_n_packaged"], 2)
        self.assertAlmostEqual(c["late_mean_packaged"], 2.1, places=4)
        self.assertAlmostEqual(c["late_mean_less_refined"], 6.0, places=4)
        self.assertAlmostEqual(c["late_mean_more_refined"], 8.0, places=4)
        self.assertAlmostEqual(c["late_pct_over_more_refined"], 0.0, places=4)


class Checks(unittest.TestCase):
    def setUp(self):
        self.results = ka.checks(ka.compute(ka.parse_tab(TEXT)))
        self.by_id = {r["id"]: r for r in self.results}

    def test_ids(self):
        self.assertEqual([r["id"] for r in self.results], ["K%d" % i for i in range(1, 30)])

    def test_selected(self):
        b = self.by_id
        self.assertFalse(b["K1"]["held"])
        self.assertEqual(b["K4"]["computed"], 7)   # 6 national zeros + Nairobi home-grown zero
        self.assertFalse(b["K7"]["held"])
        self.assertFalse(b["K15"]["held"])         # national 0% vs reported 2%
        self.assertTrue(b["K20"]["held"])          # 50% > 41%, one brand
        self.assertEqual(b["K27"]["computed"], [3, 3])
        self.assertTrue(b["K27"]["held"])
        self.assertEqual(b["K28"]["computed"], [6, 6])
        self.assertTrue(b["K28"]["held"])
        self.assertTrue(b["K29"]["held"])

    def test_predictions(self):
        p = ka.predictions(self.results)
        self.assertFalse(p["P1 counts K1-K4 all hold"])
        self.assertFalse(p["P3 K7 holds"])
        self.assertTrue(p["P4 (guess) at least one of K8-K26 fails"])
        self.assertEqual(p["n_checks"], 29)


class Main(unittest.TestCase):
    def test_main_writes_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "fixture.tab")
            with open(src, "w", encoding="utf-8") as fh:
                fh.write(TEXT)
            out = os.path.join(tmp, "out")
            self.assertEqual(ka.main(["--out-dir", out, "--tab-file", src]), 0)
            with open(os.path.join(out, "kenya_aflatoxin_check.json"), encoding="utf-8") as fh:
                report = json.load(fh)
            self.assertEqual(report["version"], "0.1.0")
            self.assertEqual(len(report["checks"]), 29)
            self.assertEqual(report["stats"]["n_analysed"], 7)


if __name__ == "__main__":
    unittest.main()
