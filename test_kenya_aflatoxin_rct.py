# Apache-2.0. Copyright 2026 Munim, Inc. Made by MV2 of Munim, Inc. with AI agents.
"""Tests for kenya_aflatoxin_rct 0.1.0 on a hand-traced 6-row fixture (not the real data)."""
import json
import os
import tempfile
import unittest

import kenya_aflatoxin_rct as kr

HEADER = ["hhid_s", "svid", "wave", "wave456", "mattrited", "eattrited", "treatment",
          "bmo_serumafb", "bmo_logserumafb", "bmo_edu3", "bmo_age", "bmo_height",
          "mch_serumflag", "mch_serumafb", "mch_logserumafb", "mch_haz06", "mch_stunted",
          "ech_sex", "ech_agemo", "ech_haz06", "ech_stunted", "ech_serumafb", "ech_logserumafb", "ech_serumflag",
          "bhhh_edu3", "bhf_scale", "bhfc_dds", "bhh_ae", "ech_bseason"]
ROWS = [
    # A: intervention, wave 2, stunted, complete covariates
    ["1", "10", "2", "0", "", "0", "1", "10", "1", "1", "20", "150", "", "", "", "", "",
     "1", "22", "-2.5", "1", "2.718282", "0.434294", "", "1", "1", "5", "3", "1"],
    # B: intervention, wave 4 (has midline), complete covariates
    ["2", "10", "4", "1", "", "0", "1", "100", "2", "2", "30", "160", "", "1", "0", "-1.0", "0",
     "0", "24", "-1.5", "0", "7.389056", "0.868589", "", "2", "2", "4", "2", "2"],
    # C: control, wave 5, dietary diversity missing
    ["3", "20", "5", "1", "", "0", "0", "1000", "3", "3", "25", "155", "", "2.718282", "0.434294", "-3.0", "1",
     "1", "21", "-1.0", "0", "20.085537", "1.302883", "", "3", "4", "", "4", "1"],
    # D: control, wave 6, attrited at endline, midline stunted flag wrong (-1.9 flagged stunted), endline flag 1
    ["4", "20", "6", "1", "", "1", "0", "10", "1", "1", "35", "165", "", "5", "0.698970", "-1.9", "1",
     "", "", "", "", "", "", "1", "1", "3", "", "", ""],
    # E: control, wave 1 (excluded from endline), wrong mother log, midline value outside waves 4-6
    ["5", "30", "1", "0", "", "0", "0", "10", "1.5", "2", "40", "158", "", "", "", "-1.2", "",
     "0", "23", "-0.5", "0", "1.0", "0", "", "2", "1", "3", "2", "1"],
    # F: arm missing, wave 3 but wave456 = 1
    ["6", "30", "3", "1", "", "0", "", "", "", "", "", "", "", "", "", "", "",
     "1", "20", "-1.0", "", "", "", "", "", "", "", "", ""],
]
TEXT = ("\t".join('"%s"' % h for h in HEADER) + "\n"
        + "\n".join("\t".join(r) for r in ROWS) + "\n")


class Fixture(unittest.TestCase):
    def test_fixture_width(self):
        for r in ROWS:
            self.assertEqual(len(r), len(HEADER))


class Helpers(unittest.TestCase):
    def test_parse(self):
        rows = kr.parse_tab(TEXT)
        self.assertEqual(len(rows), 6)
        self.assertEqual(rows[0]["ech_haz06"], -2.5)
        self.assertIsNone(rows[5]["treatment"])
        self.assertIsNone(rows[3]["ech_bseason"])

    def test_small(self):
        self.assertEqual(kr.median([3.0, 1.0, 2.0]), 2.0)
        self.assertEqual(kr.median([1.0, 2.0]), 1.5)
        self.assertIsNone(kr.sd([1.0]))
        self.assertEqual(kr.cat_pcts([1.0, 2.0, 9.0], (1.0, 2.0, 3.0)), [50.0, 50.0, 0.0])
        self.assertIsNone(kr.cat_pcts([9.0], (1.0, 2.0)))
        self.assertTrue(kr.within(1.0, 1.06, 0.06))
        self.assertFalse(kr.within(1.0, 1.07, 0.06))
        self.assertFalse(kr.within(None, 1.0, 1.0))


class Compute(unittest.TestCase):
    def setUp(self):
        self.c = kr.compute(kr.parse_tab(TEXT))

    def test_counts(self):
        c = self.c
        self.assertEqual((c["n_rows"], c["n_treatment"], c["n_control"], c["n_arm_missing"]), (6, 2, 3, 1))
        self.assertEqual(c["wave_counts"], {"1": 1, "2": 1, "3": 1, "4": 1, "5": 1, "6": 1})
        self.assertEqual((c["n_villages"], c["n_villages_t"], c["n_villages_c"], c["n_villages_mixed"]),
                         (3, 1, 2, 0))
        self.assertEqual((c["n_eattrited_t"], c["n_eattrited_c"]), (0, 1))
        self.assertEqual((c["n_endline_frame"], c["n_midline_frame"]), (4, 3))

    def test_endline(self):
        c = self.c
        self.assertAlmostEqual(c["laz_mean_end_t"], -2.0, places=4)
        self.assertAlmostEqual(c["laz_sd_end_t"], 0.707107, places=4)
        self.assertAlmostEqual(c["laz_mean_end_c"], -1.0, places=4)
        self.assertIsNone(c["laz_sd_end_c"])
        self.assertAlmostEqual(c["pct_stunted_end_t"], 50.0, places=4)
        self.assertAlmostEqual(c["pct_stunted_end_c"], 0.0, places=4)
        self.assertAlmostEqual(c["ln_afb_mean_end_t"], 1.5, places=4)
        self.assertAlmostEqual(c["log10_afb_mean_end_t"], 0.651442, places=4)
        self.assertAlmostEqual(c["afb_mean_end_t"], 5.053669, places=4)
        self.assertAlmostEqual(c["ln_afb_mean_end_c"], 3.0, places=4)
        self.assertEqual((c["n_afb_end_t"], c["n_afb_end_c"]), (2, 1))
        self.assertAlmostEqual(c["afb_median_end"], 7.389056, places=4)

    def test_midline(self):
        c = self.c
        self.assertAlmostEqual(c["laz_mean_mid_t"], -1.0, places=4)
        self.assertAlmostEqual(c["laz_mean_mid_c"], -2.45, places=4)
        self.assertAlmostEqual(c["pct_stunted_mid_c"], 100.0, places=4)
        self.assertAlmostEqual(c["pct_laz_below_cut_mid_c"], 50.0, places=4)
        self.assertAlmostEqual(c["ln_afb_mean_mid_t"], 0.0, places=4)
        self.assertAlmostEqual(c["ln_afb_mean_mid_c"], 1.304719, places=4)
        self.assertAlmostEqual(c["afb_mean_mid_c"], 3.859141, places=4)
        self.assertAlmostEqual(c["afb_median_mid"], 2.718282, places=4)

    def test_table1(self):
        c = self.c
        self.assertEqual((c["n_table1_t"], c["n_table1_c"]), (2, 1))
        self.assertAlmostEqual(c["mo_height_mean_t"], 155.0, places=4)
        self.assertAlmostEqual(c["mo_age_mean_c"], 25.0, places=4)
        self.assertEqual(c["mo_edu3_pct_t"], [50.0, 50.0, 0.0])
        self.assertEqual(c["mo_edu3_pct_c"], [0.0, 0.0, 100.0])
        self.assertAlmostEqual(c["mo_ln_afb_mean_t"], 3.453878, places=4)
        self.assertAlmostEqual(c["mo_ln_afb_mean_c"], 6.907755, places=4)
        self.assertAlmostEqual(c["ch_age_mean_t"], 23.0, places=4)
        self.assertAlmostEqual(c["pct_male_c"], 100.0, places=4)
        self.assertEqual(c["hfias_pct_t"], [50.0, 50.0, 0.0, 0.0])
        self.assertEqual(c["head_edu3_pct_c"], [0.0, 0.0, 100.0])
        self.assertEqual((c["n_complete_covariates_t"], c["n_complete_covariates_c"]), (2, 0))

    def test_consistency(self):
        c = self.c
        self.assertEqual((c["n_end_serum_rows"], c["n_end_serum_nondetect_flag"], c["n_end_serum_nonpositive"]),
                         (3, 1, 0))
        self.assertEqual(c["end_serumflag_counts"], {"1": 1})
        self.assertEqual((c["log_checked_bmo"], c["log_mismatched_bmo"]), (5, 1))
        self.assertEqual((c["log_checked_mch"], c["log_mismatched_mch"]), (3, 0))
        self.assertEqual((c["log_checked_ech"], c["log_mismatched_ech"]), (4, 0))
        self.assertEqual((c["stunt_checked_mch"], c["stunt_mismatched_mch"]), (3, 1))
        self.assertEqual(c["stunt_mismatch_haz_mch"], [-1.9])
        self.assertEqual((c["stunt_checked_ech"], c["stunt_mismatched_ech"]), (4, 0))
        self.assertEqual((c["n_midline_values_outside_waves"], c["n_wave456_disagree"]), (1, 1))


class Checks(unittest.TestCase):
    def test_fixture_checks(self):
        results = kr.checks(kr.compute(kr.parse_tab(TEXT)))
        self.assertEqual([r["id"] for r in results], ["R%d" % i for i in range(1, 26)])
        by_id = {r["id"]: r for r in results}
        self.assertEqual(by_id["R3"]["computed"], [3, 1, 2, 0])
        self.assertEqual(by_id["R22"]["computed"], [1, 0, 3])
        self.assertEqual(by_id["R23"]["computed"], [1, 12])
        self.assertEqual(by_id["R24"]["computed"], [1, 7])
        self.assertEqual(by_id["R25"]["computed"], [1, 1])
        p = kr.predictions(results)
        self.assertEqual((p["n_held"], p["n_checks"], p["n_descriptive_held"]), (0, 25, 0))
        self.assertFalse(p["P1 R1 and R3 hold"])
        self.assertFalse(p["P2 R23-R25 all hold"])
        self.assertTrue(p["P4 (guess) at least one of R2, R4 fails"])
        self.assertFalse(p["P5 R22 holds"])

    def test_tolerances(self):
        c = kr.compute(kr.parse_tab(TEXT))
        c["n_treatment"] = 687
        c["laz_mean_end_t"], c["laz_mean_end_c"] = -1.70, -1.55
        c["afb_mean_end_t"], c["afb_mean_end_c"] = 16.0, 25.0
        c["mo_edu3_pct_t"], c["mo_edu3_pct_c"] = [54.81, 29.04, 16.16], [52.3, 30.1, 17.6]
        by_id = {r["id"]: r for r in kr.checks(c)}
        self.assertTrue(by_id["R1"]["held"])
        self.assertTrue(by_id["R5"]["held"])
        self.assertFalse(by_id["R8"]["held"])
        self.assertTrue(by_id["R16"]["held"])


class Main(unittest.TestCase):
    def test_main_writes_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "fixture.tab")
            with open(src, "w", encoding="utf-8") as fh:
                fh.write(TEXT)
            out = os.path.join(tmp, "out")
            self.assertEqual(kr.main(["--out-dir", out, "--tab-file", src]), 0)
            with open(os.path.join(out, "kenya_aflatoxin_rct_check.json"), encoding="utf-8") as fh:
                report = json.load(fh)
            self.assertEqual(report["version"], "0.1.0")
            self.assertEqual(len(report["checks"]), 25)
            self.assertEqual(report["stats"]["n_rows"], 6)


if __name__ == "__main__":
    unittest.main()
