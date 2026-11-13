# Apache-2.0. Copyright 2026 Munim, Inc. Made by MV2 of Munim, Inc. with AI agents.
"""Offline tests for posthoc_rct.py on a 4-row fixture (no network)."""
import json
import math
import os
import tempfile
import unittest

import posthoc_rct as ph

HEADER = ["hhid", "svid", "treatment", "wave", "eattrited", "ech_haz06", "mch_haz06",
          "ech_serumafb", "ech_logserumafb", "ech_serumflag",
          "mch_serumafb", "mch_logserumafb", "mch_serumflag",
          "bmo_serumafb", "bmo_logserumafb", "bmo_serumflag",
          "bmo_age", "bmo_height", "bmo_edu3", "bhhh_edu3", "bhf_scale", "ech_sex", "ech_agemo"]

ROWS = [
    # row 1: arm 1, wave 4; mother log is ln(100); children's logs are log10
    {"hhid": "1", "svid": "10", "treatment": "1", "wave": "4", "eattrited": "0", "ech_haz06": "-1.0",
     "mch_haz06": "-0.5", "ech_serumafb": "100", "ech_logserumafb": "2.0", "mch_serumafb": "10",
     "mch_logserumafb": "1.0", "bmo_serumafb": "100", "bmo_logserumafb": "%.6f" % math.log(100),
     "bmo_age": "25", "bmo_height": "150", "bmo_edu3": "1", "bhhh_edu3": "1", "bhf_scale": "1",
     "ech_sex": "1", "ech_agemo": "22"},
    # row 2: arm 1, wave 2; endline flagged non-detectable with no value; mother log is log10(10)
    {"hhid": "2", "svid": "10", "treatment": "1", "wave": "2", "eattrited": "0", "ech_haz06": "-2.5",
     "ech_serumflag": "1", "bmo_serumafb": "10", "bmo_logserumafb": "1.0", "bmo_age": "30",
     "bmo_height": "160", "bmo_edu3": "2", "bhf_scale": "2", "ech_sex": "0", "ech_agemo": "20"},
    # row 3: arm 0, wave 5; endline flag 2 with a value; mother log matches neither; midline value 1 -> both
    {"hhid": "2", "svid": "20", "treatment": "0", "wave": "5", "eattrited": "1", "mch_haz06": "-1.0",
     "ech_serumafb": "5", "ech_logserumafb": "%.6f" % math.log10(5), "ech_serumflag": "2",
     "mch_serumafb": "1", "mch_logserumafb": "0", "bmo_serumafb": "50", "bmo_logserumafb": "3.0",
     "bmo_serumflag": "3", "bmo_age": "20"},
    # row 4: arm 0, wave 6; nothing measured
    {"hhid": "3", "svid": "20", "treatment": "0", "wave": "6"},
]


def fixture_text():
    lines = ["\t".join(HEADER)]
    for r in ROWS:
        lines.append("\t".join(r.get(h, "NA") for h in HEADER))
    return "\n".join(lines) + "\n"


def rows():
    return ph.parse_tab(fixture_text())


class Helpers(unittest.TestCase):
    def test_cell_value(self):
        self.assertEqual(ph.cell_value('"x"'), "x")
        self.assertIsNone(ph.cell_value("NA"))
        self.assertIsNone(ph.cell_value(""))
        self.assertEqual(ph.cell_value("1.5"), 1.5)

    def test_classify_log(self):
        self.assertEqual(ph.classify_log(100.0, 2.0), "log10")
        self.assertEqual(ph.classify_log(100.0, math.log(100.0)), "ln")
        self.assertEqual(ph.classify_log(1.0, 0.0), "both")
        self.assertEqual(ph.classify_log(100.0, 3.0), "neither")

    def test_bump(self):
        d = {}
        ph.bump(d, "a", "b")
        ph.bump(d, "a", "b")
        ph.bump(d, "c")
        self.assertEqual(d, {"a": {"b": 2}, "c": 1})


class Diagnostics(unittest.TestCase):
    def test_log_columns(self):
        lc = ph.log_columns(rows())
        self.assertEqual(lc["bmo"]["counts"], {"ln": 1, "log10": 1, "neither": 1})
        self.assertEqual(lc["bmo"]["by_treatment"], {"1": {"ln": 1, "log10": 1}, "0": {"neither": 1}})
        self.assertEqual(lc["bmo"]["by_flag"], {"missing": {"ln": 1, "log10": 1}, "3": {"neither": 1}})
        self.assertEqual(len(lc["bmo"]["neither_examples"]), 1)
        self.assertEqual(lc["bmo"]["neither_examples"][0]["value"], 50.0)
        self.assertAlmostEqual(lc["bmo"]["mean_stored_log"]["1"], (math.log(100) + 1.0) / 2, places=4)
        self.assertAlmostEqual(lc["bmo"]["mean_ln"]["1"], (math.log(100) + math.log(10)) / 2, places=4)
        self.assertAlmostEqual(lc["bmo"]["mean_log10"]["1"], 1.5, places=4)
        self.assertEqual(lc["mch"]["counts"], {"log10": 1, "both": 1})
        self.assertEqual(lc["ech"]["counts"], {"log10": 2})

    def test_serum_flags(self):
        sf = ph.serum_flags(rows())
        self.assertEqual(sf["endline"]["table"], {
            "1": {"missing": {"value": 1}, "1": {"no_value": 1}},
            "0": {"2": {"value": 1}, "missing": {"no_value": 1}}})
        self.assertEqual(sf["endline"]["flagged_with_value"], [{"treatment": 0.0, "flag": 2.0, "value": 5.0}])
        self.assertEqual(sf["midline"]["table"], {
            "1": {"missing": {"value": 1}},
            "0": {"missing": {"value": 1, "no_value": 1}}})
        self.assertEqual(sf["midline"]["flagged_with_value"], [])

    def test_arm_counts(self):
        ac = ph.arm_counts(rows())
        self.assertEqual(ac["by_treatment_wave"], {"1": {"4": 1, "2": 1}, "0": {"5": 1, "6": 1}})
        self.assertEqual(ac["no_data_rows"], {"0": 1})
        self.assertEqual(ac["presence"]["1"]["ech_haz06"], 2)
        self.assertEqual(ac["presence"]["1"]["bmo_height"], 2)
        self.assertEqual(ac["presence"]["0"]["bmo_age"], 1)

    def test_ids_and_duplicates(self):
        ids = ph.id_columns(rows())
        self.assertEqual(sorted(ids), ["hhid", "svid"])
        self.assertEqual(ids["hhid"], {"non_missing": 4, "distinct": 3, "values_repeated": 1, "max_repeat": 2})
        self.assertEqual(ids["svid"], {"non_missing": 4, "distinct": 2, "values_repeated": 2, "max_repeat": 2})
        self.assertEqual(ph.duplicate_rows(rows()), 0)
        self.assertEqual(ph.duplicate_rows(rows() + rows()[:1]), 1)

    def test_height_frames(self):
        hf = ph.height_frames(rows())
        self.assertEqual(hf["all_rows"]["1"], {"n_rows": 2, "n_height": 2, "mean_height": 155.0})
        self.assertEqual(hf["all_rows"]["0"], {"n_rows": 2, "n_height": 0, "mean_height": None})
        self.assertEqual(hf["table1_frame_endline_laz"]["1"]["n_rows"], 2)
        self.assertEqual(hf["table1_frame_endline_laz"]["0"]["n_rows"], 0)
        self.assertEqual(hf["table1_frame_not_attrited"]["1"]["n_rows"], 2)
        self.assertEqual(hf["table1_frame_strict_covariates"]["1"],
                         {"n_rows": 1, "n_height": 1, "mean_height": 150.0})
        self.assertEqual(hf["paper_table1_n"], {"1": 489, "0": 392})


class Main(unittest.TestCase):
    def test_main_writes_report(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "fixture.tab")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(fixture_text())
            self.assertEqual(ph.main(["--out-dir", os.path.join(d, "out"), "--tab-file", path]), 0)
            with open(os.path.join(d, "out", "posthoc_rct.json"), encoding="utf-8") as fh:
                report = json.load(fh)
        self.assertTrue(report["post_hoc"])
        self.assertFalse(report["sha256_matches_graded_file"])
        self.assertEqual(report["n_rows"], 4)
        self.assertIsNone(report["source_url"])
        self.assertEqual(report["log_columns"]["ech"]["counts"], {"log10": 2})


if __name__ == "__main__":
    unittest.main()
