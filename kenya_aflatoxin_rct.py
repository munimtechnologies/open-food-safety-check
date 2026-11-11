# Apache-2.0. Copyright 2026 Munim, Inc. Made by MV2 of Munim, Inc. with AI agents.
"""kenya_aflatoxin_rct 0.1.0: re-computes, from the trial's own open data, the descriptive numbers published for

  Hoffmann V, Jones K, Leroy JL (2018). The impact of reducing dietary aflatoxin exposure on child linear
  growth: a cluster randomised controlled trial in Kenya. BMJ Global Health 3(6): e000983 (CC BY 4.0).
  doi:10.1136/bmjgh-2018-000983

  Data: International Food Policy Research Institute (IFPRI), 2019, Replication Data for: The Impact of
  Reducing Dietary Aflatoxin Exposure on Child Linear Growth: A Cluster Randomized Controlled Trial in Kenya.
  Washington, DC: IFPRI [dataset], Harvard Dataverse, V1.1, doi:10.7910/DVN/OHIOYR (CC BY 4.0).
  File aflatoxin_child_Kenya.tab (Dataverse file id 3347337).

and grades each published number against the data, with the rules fixed in docs/kenya-aflatoxin-rct-0.1.0.md
before the data were read. Standard library only. IFPRI bears no responsibility for these analyses.

  python kenya_aflatoxin_rct.py --out-dir OUT [--tab-file PATH]   (no --tab-file: downloads DATA_URL)
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
MISSING = ("", ".", "NA", "NaN", "nan")
ARM_TAGS = ((1.0, "t"), (0.0, "c"))      # treatment = 1, control = 0; every [t, c] pair is in this order
ARMS = (1.0, 0.0)
EXCLUDED_ENDLINE_WAVE = 1.0               # "all enrolment waves (excluding wave 1) combined"
MIDLINE_WAVES = (4.0, 5.0, 6.0)           # midline was run for waves 4-6 only
STUNT_CUT = -2.0
LOG_TOLERANCE = 0.01
COVARIATES = ("bmo_age", "bmo_height", "bmo_edu3", "bhhh_edu3", "bhf_scale", "bhfc_dds", "bhh_ae",
              "ech_sex", "ech_agemo", "ech_bseason")
# Tolerances, fixed before the data were read (about one standard error of an arm mean, to absorb the
# paper's unknown covariate-completeness exclusions; see the pre-registration).
TOL_Z = 0.06
TOL_LN = 0.10
TOL_PCT = 3.0
TOL_REL = 0.12
TOL_CM = 0.4
TOL_YEARS = 0.4
TOL_MONTHS = 0.25
TOL_MEDIAN = 0.4


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


def vals(rows, name):
    return [val(r, name) for r in rows if val(r, name) is not None]


def arm_of(row):
    t = val(row, "treatment")
    return t if t in ARMS else None


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def sd(xs):
    if len(xs) < 2:
        return None
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def median(xs):
    xs = sorted(xs)
    if not xs:
        return None
    mid = len(xs) // 2
    return xs[mid] if len(xs) % 2 else (xs[mid - 1] + xs[mid]) / 2.0


def pct(xs, test):
    return 100.0 * sum(1 for x in xs if test(x)) / len(xs) if xs else None


def cat_pcts(values, codes):
    """Percent of values equal to each code; denominator = values that are one of the codes."""
    usable = [v for v in values if v in codes]
    if not usable:
        return None
    return [100.0 * sum(1 for v in usable if v == code) / len(usable) for code in codes]


def compute(rows):
    """Every statistic the checks need."""
    out = {"n_rows": len(rows)}
    armed = [r for r in rows if arm_of(r) is not None]
    out["n_treatment"] = sum(1 for r in armed if arm_of(r) == 1.0)
    out["n_control"] = sum(1 for r in armed if arm_of(r) == 0.0)
    out["n_arm_missing"] = len(rows) - len(armed)
    waves = {}
    for r in rows:
        w = val(r, "wave")
        key = "missing" if w is None else "%g" % w
        waves[key] = waves.get(key, 0) + 1
    out["wave_counts"] = waves
    village_arms = {}
    for r in armed:
        v = r.get("svid")
        if v is not None:
            village_arms.setdefault(str(v), set()).add(arm_of(r))
    out["n_villages"] = len(village_arms)
    out["n_villages_t"] = sum(1 for s in village_arms.values() if s == {1.0})
    out["n_villages_c"] = sum(1 for s in village_arms.values() if s == {0.0})
    out["n_villages_mixed"] = sum(1 for s in village_arms.values() if len(s) > 1)
    for arm, tag in ARM_TAGS:
        a = [r for r in armed if arm_of(r) == arm]
        out["n_eattrited_" + tag] = sum(1 for r in a if val(r, "eattrited") == 1.0)
        out["n_mattrited_" + tag] = sum(1 for r in a if val(r, "mattrited") == 1.0)
    end = [r for r in armed if val(r, "wave") != EXCLUDED_ENDLINE_WAVE]
    mid = [r for r in armed if val(r, "wave") in MIDLINE_WAVES]
    out["n_endline_frame"], out["n_midline_frame"] = len(end), len(mid)
    for period, frame, p in (("end", end, "ech_"), ("mid", mid, "mch_")):
        for arm, tag in ARM_TAGS:
            a = [r for r in frame if arm_of(r) == arm]
            k = "_%s_%s" % (period, tag)
            laz = vals(a, p + "haz06")
            stunted = [val(r, p + "stunted") for r in a
                       if val(r, p + "haz06") is not None and val(r, p + "stunted") is not None]
            pos = [v for v in vals(a, p + "serumafb") if v > 0]
            unflagged = [val(r, p + "serumafb") for r in a if val(r, p + "serumafb") is not None
                         and val(r, p + "serumafb") > 0 and val(r, p + "serumflag") is None]
            out["n_laz" + k], out["laz_mean" + k], out["laz_sd" + k] = len(laz), mean(laz), sd(laz)
            out["n_laz_abs_gt6" + k] = sum(1 for v in laz if abs(v) > 6)
            out["n_stunted_rows" + k] = len(stunted)
            out["pct_stunted" + k] = pct(stunted, lambda v: v == 1.0)
            out["pct_laz_below_cut" + k] = pct(laz, lambda v: v < STUNT_CUT)
            out["n_afb" + k] = len(pos)
            out["n_afb_nonpositive" + k] = len(vals(a, p + "serumafb")) - len(pos)
            out["ln_afb_mean" + k] = mean([math.log(v) for v in pos])
            out["ln_afb_sd" + k] = sd([math.log(v) for v in pos])
            out["log10_afb_mean" + k] = mean([math.log10(v) for v in pos])
            out["afb_mean" + k], out["afb_sd" + k] = mean(pos), sd(pos)
            out["n_afb_unflagged" + k] = len(unflagged)
            out["ln_afb_mean_unflagged" + k] = mean([math.log(v) for v in unflagged])
        out["afb_median_" + period] = median([v for v in vals(frame, p + "serumafb") if v > 0])
    # Table 1 frame: endline rows with an endline LAZ (the paper's Table 1 is on its LAZ analysis sample).
    for arm, tag in ARM_TAGS:
        s = [r for r in end if arm_of(r) == arm and val(r, "ech_haz06") is not None]
        k = "_" + tag
        out["n_table1" + k] = len(s)
        out["mo_height_mean" + k] = mean(vals(s, "bmo_height"))
        out["mo_age_mean" + k] = mean(vals(s, "bmo_age"))
        out["mo_edu3_pct" + k] = cat_pcts(vals(s, "bmo_edu3"), (1.0, 2.0, 3.0))
        mo = [v for v in vals(s, "bmo_serumafb") if v > 0]
        out["n_mo_afb" + k] = len(mo)
        out["mo_ln_afb_mean" + k] = mean([math.log(v) for v in mo])
        out["ch_age_mean" + k] = mean(vals(s, "ech_agemo"))
        out["pct_male" + k] = pct(vals(s, "ech_sex"), lambda v: v == 1.0)
        out["hfias_pct" + k] = cat_pcts(vals(s, "bhf_scale"), (1.0, 2.0, 3.0, 4.0))
        out["head_edu3_pct" + k] = cat_pcts(vals(s, "bhhh_edu3"), (1.0, 2.0, 3.0))
        out["n_complete_covariates" + k] = sum(1 for r in s if all(val(r, c) is not None for c in COVARIATES))
    # Endline serum detectability.
    det = [r for r in end if val(r, "ech_serumafb") is not None]
    out["n_end_serum_rows"] = len(det)
    out["n_end_serum_nondetect_flag"] = sum(1 for r in end if val(r, "ech_serumflag") == 1.0)
    out["n_end_serum_nonpositive"] = sum(1 for r in det if val(r, "ech_serumafb") <= 0)
    out["end_serum_min"] = min(vals(det, "ech_serumafb")) if det else None
    flags = {}
    for r in end:
        f = val(r, "ech_serumflag")
        if f is not None:
            flags["%g" % f] = flags.get("%g" % f, 0) + 1
    out["end_serumflag_counts"] = flags
    # Internal consistency of the log10 columns and the stunting flags.
    for p in ("bmo", "mch", "ech"):
        checked = mismatched = 0
        for r in rows:
            v = val(r, p + "_serumafb")
            if v is not None and v > 0:
                checked += 1
                lg = val(r, p + "_logserumafb")
                if lg is None or abs(math.log10(v) - lg) > LOG_TOLERANCE:
                    mismatched += 1
        out["log_checked_" + p], out["log_mismatched_" + p] = checked, mismatched
    for p in ("mch", "ech"):
        checked = mismatched = 0
        examples = []
        for r in rows:
            z, s = val(r, p + "_haz06"), val(r, p + "_stunted")
            if z is not None and s is not None:
                checked += 1
                if (z < STUNT_CUT) != (s == 1.0):
                    mismatched += 1
                    if len(examples) < 10:
                        examples.append(z)
        out["stunt_checked_" + p], out["stunt_mismatched_" + p] = checked, mismatched
        out["stunt_mismatch_haz_" + p] = examples
    out["n_midline_values_outside_waves"] = sum(
        1 for r in rows if (val(r, "mch_haz06") is not None or val(r, "mch_serumafb") is not None)
        and val(r, "wave") not in MIDLINE_WAVES)
    out["n_wave456_disagree"] = sum(
        1 for r in rows if val(r, "wave") is not None and val(r, "wave456") is not None
        and (val(r, "wave") in MIDLINE_WAVES) != (val(r, "wave456") == 1.0))
    return out


def within(value, target, tol):
    return value is not None and abs(value - target) <= tol + 1e-9


def checks(c):
    """The 25 graded checks of docs/kenya-aflatoxin-rct-0.1.0.md: list of dicts."""
    out = []

    def add(cid, claim, reported, computed, held):
        out.append({"id": cid, "claim": claim, "reported": reported, "computed": computed, "held": bool(held)})

    def pair(cid, claim, base, reported, tol, relative=False):
        computed = [c[base + "_t"], c[base + "_c"]]
        held = all(within(v, r, abs(r) * tol if relative else tol) for v, r in zip(computed, reported))
        add(cid, claim, reported, computed, held)

    def cats(cid, claim, base, rep_t, rep_c, tol):
        ct, cc = c[base + "_t"], c[base + "_c"]
        held = (ct is not None and cc is not None
                and all(within(v, r, tol) for v, r in zip(ct + cc, rep_t + rep_c)))
        add(cid, claim, [rep_t, rep_c], [ct, cc], held)

    add("R1", "687 intervention children enrolled (rows with treatment = 1)", 687, c["n_treatment"],
        c["n_treatment"] == 687)
    add("R2", "control children enrolled: 532 (paper) or 536 (dataset description)", [532, 536], c["n_control"],
        c["n_control"] in (532, 536))
    computed = [c["n_villages"], c["n_villages_t"], c["n_villages_c"], c["n_villages_mixed"]]
    add("R3", "56 villages, 28 per arm, one arm per village", [56, 28, 28, 0], computed, computed == [56, 28, 28, 0])
    computed = [c["n_eattrited_t"], c["n_eattrited_c"]]
    add("R4", "lost to follow-up at endline: 148 intervention, 118 control (eattrited = 1)", [148, 118],
        computed, computed == [148, 118])
    pair("R5", "endline LAZ mean, intervention / control (within 0.06)", "laz_mean_end", [-1.68, -1.59], TOL_Z)
    pair("R6", "endline stunting %, intervention / control (within 3 points)", "pct_stunted_end", [39.26, 35.71],
         TOL_PCT)
    pair("R7", "endline ln serum AFB1-lysine mean (within 0.10)", "ln_afb_mean_end", [1.78, 2.01], TOL_LN)
    pair("R8", "endline serum AFB1-lysine mean, pg/mg albumin (within 12%)", "afb_mean_end", [14.79, 22.19],
         TOL_REL, relative=True)
    add("R9", "pooled endline serum AFB1-lysine median 6.1 pg/mg (within 0.4)", 6.1, c["afb_median_end"],
        within(c["afb_median_end"], 6.1, TOL_MEDIAN))
    pair("R10", "midline LAZ mean (within 0.06)", "laz_mean_mid", [-1.17, -1.32], TOL_Z)
    pair("R11", "midline stunting % (within 3 points)", "pct_stunted_mid", [20.00, 26.57], TOL_PCT)
    pair("R12", "midline ln serum AFB1-lysine mean (within 0.10)", "ln_afb_mean_mid", [1.54, 1.60], TOL_LN)
    pair("R13", "midline serum AFB1-lysine mean, pg/mg (within 12%)", "afb_mean_mid", [9.83, 16.12], TOL_REL,
         relative=True)
    pair("R14", "Table 1 mother height, cm (within 0.4)", "mo_height_mean", [157.47, 158.10], TOL_CM)
    pair("R15", "Table 1 mother age, years (within 0.4)", "mo_age_mean", [25.74, 25.70], TOL_YEARS)
    cats("R16", "Table 1 mother education %, 3 categories (within 3 points)", "mo_edu3_pct",
         [54.81, 29.04, 16.16], [52.3, 30.1, 17.6], TOL_PCT)
    pair("R17", "Table 1 mother ln serum AFB1-lysine (within 0.10)", "mo_ln_afb_mean", [2.69, 2.74], TOL_LN)
    pair("R18", "Table 1 child endline age, months (within 0.25)", "ch_age_mean", [22.13, 22.02], TOL_MONTHS)
    pair("R19", "Table 1 child male % (within 3 points)", "pct_male", [51.12, 51.79], TOL_PCT)
    cats("R20", "Table 1 HFIAS food-security %, 4 categories (within 3 points)", "hfias_pct",
         [19.02, 14.31, 37.63, 29.04], [17.35, 13.52, 36.48, 32.65], TOL_PCT)
    cats("R21", "Table 1 household-head education %, 3 categories (within 3 points)", "head_edu3_pct",
         [56.85, 27.81, 15.34], [51.79, 26.79, 21.43], TOL_PCT)
    computed = [c["n_end_serum_nondetect_flag"], c["n_end_serum_nonpositive"], c["n_end_serum_rows"]]
    add("R22", "adduct detectable in all endline child samples (no non-detectable flag, no value <= 0)",
        [0, 0], computed, computed[0] == 0 and computed[1] == 0 and computed[2] > 0)
    mism = sum(c["log_mismatched_" + p] for p in ("bmo", "mch", "ech"))
    chk = sum(c["log_checked_" + p] for p in ("bmo", "mch", "ech"))
    add("R23", "log10 serum columns equal log10 of the serum values (within 0.01)", 0, [mism, chk],
        mism == 0 and chk > 0)
    mism = sum(c["stunt_mismatched_" + p] for p in ("mch", "ech"))
    chk = sum(c["stunt_checked_" + p] for p in ("mch", "ech"))
    add("R24", "stunted flag = (height-for-age z < -2) on every row with both", 0, [mism, chk],
        mism == 0 and chk > 0)
    computed = [c["n_midline_values_outside_waves"], c["n_wave456_disagree"]]
    add("R25", "midline values only in waves 4-6, and wave456 agrees with wave", [0, 0], computed,
        computed == [0, 0])
    return out


def predictions(results):
    held = {r["id"]: r["held"] for r in results}
    n_held = sum(1 for r in results if r["held"])
    descriptive = ["R%d" % i for i in range(5, 22)]
    return {
        "P1 R1 and R3 hold": held["R1"] and held["R3"],
        "P2 R23-R25 all hold": all(held[k] for k in ("R23", "R24", "R25")),
        "P3 at least 13 of the 17 descriptive checks R5-R21 hold": sum(1 for k in descriptive if held[k]) >= 13,
        "P4 (guess) at least one of R2, R4 fails": not (held["R2"] and held["R4"]),
        "P5 R22 holds": held["R22"],
        "n_descriptive_held": sum(1 for k in descriptive if held[k]),
        "n_held": n_held,
        "n_checks": len(results),
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
    else:
        req = urllib.request.Request(args.url, headers={
            "User-Agent": "kenya-aflatoxin-rct-check/0.1.0 (mv2@munimtech.com)"})
        with urllib.request.urlopen(req, timeout=180) as resp:
            raw = resp.read()
        with open(os.path.join(args.out_dir, "aflatoxin_child_Kenya.tab"), "wb") as fh:
            fh.write(raw)
    rows = parse_tab(raw.decode("utf-8-sig", "replace"))
    stats = compute(rows)
    results = checks(stats)
    report = {
        "version": VERSION,
        "source_url": None if args.tab_file else args.url,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "n_columns": len(rows[0]) if rows else 0,
        "stats": stats,
        "checks": results,
        "predictions": predictions(results),
    }
    path = os.path.join(args.out_dir, "kenya_aflatoxin_rct_check.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1, sort_keys=True, default=str)
    for r in results:
        print("%-4s %-5s reported %s computed %s  %s" % (
            r["id"], "held" if r["held"] else "FAIL", r["reported"], r["computed"], r["claim"]))
    print(json.dumps(report["predictions"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
