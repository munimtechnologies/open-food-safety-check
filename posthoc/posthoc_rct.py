# Apache-2.0. Copyright 2026 Munim, Inc. Made by MV2 of Munim, Inc. with AI agents.
"""posthoc_rct 0.1.0: POST HOC diagnostics for the misses of kenya-aflatoxin-rct 0.1.0.

Not pre-registered. It runs after the graded result (docs/kenya-aflatoxin-rct-0.1.0-result.md) and only
describes the file, to explain the misses R1/R2 (arm counts), R14 (mother height), R22 (non-detectable
endline samples) and R23 (log columns). Nothing here changes a grade.

Data: IFPRI 2019, Replication Data for: The Impact of Reducing Dietary Aflatoxin Exposure on Child Linear
Growth: A Cluster Randomized Controlled Trial in Kenya, Harvard Dataverse V1.1, doi:10.7910/DVN/OHIOYR
(CC BY 4.0), file aflatoxin_child_Kenya.tab (id 3347337). IFPRI bears no responsibility for these analyses.

  python posthoc_rct.py --out-dir OUT [--tab-file PATH]   (no --tab-file: downloads DATA_URL)
"""
import argparse
import hashlib
import json
import math
import os
import sys
import urllib.request

VERSION = "0.1.0"
DATA_URL = "https://dataverse.harvard.edu/api/access/datafile/3347337"
GRADED_SHA256 = "d48ac94dc165930f2ec2dff546b31b9abc70ee28155a767ffe781a3b0504defe"
MISSING = ("", ".", "NA", "NaN", "nan")
LOG_TOL = 0.01
MIDLINE_WAVES = (4.0, 5.0, 6.0)
PAPER_TABLE1_N = {"1": 489, "0": 392}
PAPER_MOTHER_HEIGHT = {"1": 157.47, "0": 158.10}
STRICT_COVARIATES = ("bmo_height", "bmo_age", "bmo_edu3", "bhhh_edu3", "bhf_scale", "ech_sex", "ech_agemo")
PRESENCE_COLUMNS = ("ech_haz06", "mch_haz06", "ech_serumafb", "mch_serumafb", "bmo_serumafb", "bmo_age",
                    "bmo_height")


def cell_value(cell):
    """A tab cell as float, None (missing) or str."""
    cell = cell.strip()
    if len(cell) >= 2 and cell[0] == '"' and cell[-1] == '"':
        cell = cell[1:-1]
    if cell in MISSING:
        return None
    try:
        value = float(cell)
    except ValueError:
        return cell
    if math.isnan(value):
        return None
    if math.isinf(value):
        return cell
    return value


def parse_tab(text):
    """Rows of a Dataverse tab file (header line first) as dicts of name -> float, str or None."""
    lines = [ln for ln in text.splitlines() if ln.strip()]
    names = [h.strip().strip('"') for h in lines[0].split("\t")]
    rows = []
    for ln in lines[1:]:
        cells = ln.split("\t")
        rows.append({name: cell_value(cells[i]) if i < len(cells) else None for i, name in enumerate(names)})
    return rows


def val(row, name):
    value = row.get(name)
    return value if isinstance(value, float) else None


def key(x):
    return "missing" if x is None else "%g" % x


def bump(d, *keys):
    """d[k1][k2]...[kn] += 1, creating the nested dicts."""
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    d[keys[-1]] = d.get(keys[-1], 0) + 1


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def classify_log(value, stored):
    """Which log a stored log value matches for a value > 0: 'log10', 'ln', 'both' or 'neither'."""
    by10 = abs(math.log10(value) - stored) <= LOG_TOL
    byln = abs(math.log(value) - stored) <= LOG_TOL
    if by10 and byln:
        return "both"
    if by10:
        return "log10"
    if byln:
        return "ln"
    return "neither"


def log_columns(rows):
    """For each serum column, which log each stored log value matches, overall and by wave, arm and flag."""
    out = {}
    for p in ("bmo", "mch", "ech"):
        res = {"counts": {}, "by_wave": {}, "by_treatment": {}, "by_flag": {}, "neither_examples": [],
               "mean_stored_log": {}, "mean_ln": {}, "mean_log10": {}}
        sums = {}
        for r in rows:
            v = val(r, p + "_serumafb")
            if v is None or v <= 0:
                continue
            stored = val(r, p + "_logserumafb")
            kind = "log_missing" if stored is None else classify_log(v, stored)
            bump(res["counts"], kind)
            bump(res["by_wave"], key(val(r, "wave")), kind)
            bump(res["by_treatment"], key(val(r, "treatment")), kind)
            bump(res["by_flag"], key(val(r, p + "_serumflag")), kind)
            if kind == "neither" and len(res["neither_examples"]) < 15:
                res["neither_examples"].append({"value": v, "stored_log": stored, "log10": math.log10(v),
                                                "ln": math.log(v)})
            if stored is not None:
                s = sums.setdefault(key(val(r, "treatment")), [0, 0.0, 0.0, 0.0])
                s[0] += 1
                s[1] += stored
                s[2] += math.log(v)
                s[3] += math.log10(v)
        for arm, s in sums.items():
            res["mean_stored_log"][arm] = s[1] / s[0]
            res["mean_ln"][arm] = s[2] / s[0]
            res["mean_log10"][arm] = s[3] / s[0]
        out[p] = res
    return out


def serum_flags(rows):
    """Serum flag x value present, by arm: endline frame (wave != 1) and midline frame (waves 4-6)."""
    out = {}
    frames = (("ech", "endline", lambda w: w != 1.0), ("mch", "midline", lambda w: w in MIDLINE_WAVES))
    for p, label, keep in frames:
        table = {}
        flagged_with_value = []
        for r in rows:
            if not keep(val(r, "wave")):
                continue
            f = val(r, p + "_serumflag")
            v = val(r, p + "_serumafb")
            bump(table, key(val(r, "treatment")), key(f), "value" if v is not None else "no_value")
            if f is not None and v is not None:
                flagged_with_value.append({"treatment": val(r, "treatment"), "flag": f, "value": v})
        out[label] = {"table": table, "flagged_with_value": flagged_with_value}
    return out


def arm_counts(rows):
    """Rows by arm and wave, which key columns each arm has, and rows with none of them."""
    out = {"by_treatment_wave": {}, "no_data_rows": {}, "presence": {}}
    for r in rows:
        arm = key(val(r, "treatment"))
        bump(out["by_treatment_wave"], arm, key(val(r, "wave")))
        present = [c for c in PRESENCE_COLUMNS if val(r, c) is not None]
        for c in present:
            bump(out["presence"], arm, c)
        if not present:
            bump(out["no_data_rows"], arm)
    return out


def id_columns(rows):
    """Distinct and repeated values of every column whose name ends in 'id'."""
    names = [n for n in (rows[0].keys() if rows else []) if n.lower().endswith("id")]
    out = {}
    for n in names:
        counts = {}
        for r in rows:
            x = r.get(n)
            if x is None:
                continue
            counts[str(x)] = counts.get(str(x), 0) + 1
        out[n] = {"non_missing": sum(counts.values()), "distinct": len(counts),
                  "values_repeated": sum(1 for c in counts.values() if c > 1),
                  "max_repeat": max(counts.values()) if counts else 0}
    return out


def duplicate_rows(rows):
    """Rows that are exact copies of an earlier row."""
    seen = {}
    for r in rows:
        k = json.dumps(r, sort_keys=True, default=str)
        seen[k] = seen.get(k, 0) + 1
    return sum(c - 1 for c in seen.values() if c > 1)


def height_frames(rows):
    """Mean mother height by arm under the graded Table 1 frame and narrower ones."""
    def endline_laz(r):
        return val(r, "wave") != 1.0 and val(r, "ech_haz06") is not None

    frames = (
        ("all_rows", lambda r: True),
        ("table1_frame_endline_laz", endline_laz),
        ("table1_frame_not_attrited", lambda r: endline_laz(r) and val(r, "eattrited") != 1.0),
        ("table1_frame_strict_covariates",
         lambda r: endline_laz(r) and all(val(r, c) is not None for c in STRICT_COVARIATES)),
    )
    out = {"paper_table1_n": PAPER_TABLE1_N, "paper_mean_height": PAPER_MOTHER_HEIGHT}
    for name, keep in frames:
        res = {}
        for arm in (1.0, 0.0):
            kept = [r for r in rows if val(r, "treatment") == arm and keep(r)]
            hs = vals_of(kept, "bmo_height")
            res["%g" % arm] = {"n_rows": len(kept), "n_height": len(hs), "mean_height": mean(hs)}
        out[name] = res
    return out


def vals_of(rows, name):
    return [val(r, name) for r in rows if val(r, name) is not None]


def report_for(raw, source_url):
    sha = hashlib.sha256(raw).hexdigest()
    rows = parse_tab(raw.decode("utf-8-sig", "replace"))
    return {
        "version": VERSION,
        "post_hoc": True,
        "note": "Post hoc diagnostics, not pre-registered; they do not change any grade.",
        "source_url": source_url,
        "sha256": sha,
        "sha256_matches_graded_file": sha == GRADED_SHA256,
        "n_rows": len(rows),
        "log_columns": log_columns(rows),
        "serum_flags": serum_flags(rows),
        "arm_counts": arm_counts(rows),
        "id_columns": id_columns(rows),
        "duplicate_rows": duplicate_rows(rows),
        "mother_height_frames": height_frames(rows),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--tab-file")
    ap.add_argument("--url", default=DATA_URL)
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    if args.tab_file:
        with open(args.tab_file, "rb") as fh:
            raw = fh.read()
        source = None
    else:
        req = urllib.request.Request(args.url, headers={
            "User-Agent": "kenya-aflatoxin-rct-posthoc/0.1.0 (mv2@munimtech.com)"})
        with urllib.request.urlopen(req, timeout=180) as resp:
            raw = resp.read()
        source = args.url
    report = report_for(raw, source)
    with open(os.path.join(args.out_dir, "posthoc_rct.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1, sort_keys=True, default=str)
    print("POST HOC (not pre-registered). sha256 matches graded file: %s; rows %d"
          % (report["sha256_matches_graded_file"], report["n_rows"]))
    for p in ("bmo", "mch", "ech"):
        lc = report["log_columns"][p]
        print("R23 %s log column: %s by_treatment %s mean stored %s ln %s log10 %s" % (
            p, json.dumps(lc["counts"], sort_keys=True), json.dumps(lc["by_treatment"], sort_keys=True),
            json.dumps(lc["mean_stored_log"], sort_keys=True), json.dumps(lc["mean_ln"], sort_keys=True),
            json.dumps(lc["mean_log10"], sort_keys=True)))
        print("R23 %s by wave %s by flag %s" % (p, json.dumps(lc["by_wave"], sort_keys=True),
                                                json.dumps(lc["by_flag"], sort_keys=True)))
    for label in ("endline", "midline"):
        sf = report["serum_flags"][label]
        print("R22 %s flag x value by arm %s flagged_with_value %s" % (
            label, json.dumps(sf["table"], sort_keys=True), json.dumps(sf["flagged_with_value"], default=str)))
    ac = report["arm_counts"]
    print("R1/R2 rows by arm x wave %s no-data rows %s" % (json.dumps(ac["by_treatment_wave"], sort_keys=True),
                                                         json.dumps(ac["no_data_rows"], sort_keys=True)))
    print("R1/R2 id columns %s duplicate rows %d" % (json.dumps(report["id_columns"], sort_keys=True),
                                                    report["duplicate_rows"]))
    print("R14 mother height frames %s" % json.dumps(report["mother_height_frames"], sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
