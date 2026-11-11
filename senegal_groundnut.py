# Apache-2.0. Copyright 2026 Munim, Inc. Made by MV2 of Munim, Inc. with AI agents.
"""senegal_groundnut 0.1.0: re-computes, from the survey's own open data, the headline numbers published for

  the Feed the Future Innovation Lab for Food Safety (FSIL) pilot on groundnuts stored by 250 smallholder
  households in Senegal's Peanut Basin (Kaolack area), surveyed in 2020 (Purdue University and ISRA):
  Y. Arias-Granada, "Food for Thought: Contaminants in Groundnut", FSIL Program Updates (Purdue), 2020/2021,
  https://ag.purdue.edu/food-safety-innovation-lab/food-for-thought-contaminants-in-groundnut/

  Data: Bauchet, Jonathan (2021). Testing cost-effective interventions to reduce E. coli and other
  contamination in Senegalese groundnut production and consumption. Harvard Dataverse, V1.1,
  doi:10.7910/DVN/ACKHW5 (CC0 1.0). File hhfinal_share.tab (Dataverse file id 4880423).

and grades each published number against the data, with the rules fixed in docs/senegal-groundnut-0.1.0.md
before the data were read. Standard library only.

  python senegal_groundnut.py --out-dir OUT [--tab-file PATH]   (no --tab-file: downloads DATA_URL)
"""
import argparse
import hashlib
import json
import math
import os
import sys
import urllib.request
from decimal import ROUND_HALF_UP, Decimal

VERSION = "0.1.0"
DATA_URL = "https://dataverse.harvard.edu/api/access/datafile/4880423"
MISSING = ("", ".", "NA", "NaN", "nan")
KEY_FIELDS = ("interview__key", "interview__id")
ORGANISMS = ("eb", "coli", "mold")   # Enterobacteriaceae, coliforms, moulds (codebook suffixes)
LAB = ("aflatoxin",) + tuple("%s_%s" % (p, o) for o in ORGANISMS for p in ("cfug", "log10cfug"))
SURVEY = ("consent", "aflx_heard", "bac_heard", "prod_consall__1")
CENSOR_PPB = 100.0     # the codebook: "Aflatoxins levels (censored at 100 ppb)"
EU_PPB = 4.0           # EU limit for total aflatoxins in groundnuts for direct consumption
LOG_THRESHOLD = 1.0       # 1 log10 CFU/g, the US limit the FSIL post uses for both coliforms and Enterobacteriaceae
LOG_TOLERANCE = 0.01
AVERAGE_TOLERANCE = 0.5


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


def rounds_to(value, reported):
    """True if value, rounded half-up to the decimals written in the string `reported`, equals it."""
    if value is None:
        return False
    places = len(reported.split(".")[1]) if "." in reported else 0
    quantum = Decimal(1).scaleb(-places)
    return Decimal(repr(float(value))).quantize(quantum, rounding=ROUND_HALF_UP) == Decimal(reported)


def num(value):
    return value if isinstance(value, float) else None


def share(values, test):
    """(percent of usable values passing test, number usable). Usable = numeric and >= 0 (negative codes
    such as -999 are 'don't know'/'refused' style codes, not answers)."""
    usable = [v for v in values if v is not None and v >= 0]
    if not usable:
        return None, 0
    return 100.0 * sum(1 for v in usable if test(v)) / len(usable), len(usable)


def median(values):
    values = sorted(values)
    if not values:
        return None
    mid = len(values) // 2
    return values[mid] if len(values) % 2 else (values[mid - 1] + values[mid]) / 2.0


def households(rows):
    """Rows grouped by interview key, in file order. Rows with no key are their own group."""
    groups = {}
    for i, r in enumerate(rows):
        key = None
        for field in KEY_FIELDS:
            if r.get(field) is not None:
                key = str(r[field])
                break
        groups.setdefault(key if key is not None else "row%d" % i, []).append(r)
    return groups


def compute(rows):
    """Every statistic the checks need. Household values = first numeric value among the household's rows."""
    groups = households(rows)
    conflicts = {name: 0 for name in LAB}
    hh = []
    for group in groups.values():
        rec = {}
        for name in LAB + SURVEY:
            vals = [num(r.get(name)) for r in group if num(r.get(name)) is not None]
            rec[name] = vals[0] if vals else None
            if name in conflicts and len(set(vals)) > 1:
                conflicts[name] += 1
        hh.append(rec)
    col = lambda name: [rec[name] for rec in hh]
    out = {
        "n_rows": len(rows),
        "n_households": len(groups),
        "rows_per_household_max": max((len(g) for g in groups.values()), default=0),
        "n_consent1": sum(1 for v in col("consent") if v == 1.0),
        "lab_conflicts": conflicts,
    }
    for name in SURVEY[1:]:
        values = col(name)
        out["pct_" + name], out["n_" + name] = share(values, lambda v: v == 1.0)
        out["n_negative_" + name] = sum(1 for v in values if v is not None and v < 0)
        out["values_" + name] = sorted(set(v for v in values if v is not None))[:10]
        yes = sum(1 for v in values if v == 1.0)
        out["pct_all_households_" + name] = 100.0 * yes / len(hh) if hh else None
    afla = col("aflatoxin")
    usable = [v for v in afla if v is not None and v >= 0]
    out["n_aflatoxin"] = len(usable)
    out["n_negative_aflatoxin"] = sum(1 for v in afla if v is not None and v < 0)
    out["pct_afla_lt4"] = share(afla, lambda v: v < EU_PPB)[0]
    out["pct_afla_le4"] = share(afla, lambda v: v <= EU_PPB)[0]
    out["pct_afla_ge100"] = share(afla, lambda v: v >= CENSOR_PPB)[0]
    out["pct_afla_gt100"] = share(afla, lambda v: v > CENSOR_PPB)[0]
    out["pct_afla_gt20"] = share(afla, lambda v: v > 20.0)[0]
    out["pct_afla_gt10"] = share(afla, lambda v: v > 10.0)[0]
    out["n_afla_zero"] = sum(1 for v in usable if v == 0.0)
    out["afla_min"] = min(usable) if usable else None
    out["afla_max"] = max(usable) if usable else None
    out["afla_median"] = median(usable)
    out["afla_smallest_values"] = sorted(set(usable))[:15]
    for org in ORGANISMS:
        logs = col("log10cfug_" + org)
        cfu = col("cfug_" + org)
        out["pct_log_gt1_" + org], out["n_log_" + org] = share(logs, lambda v: v > LOG_THRESHOLD)
        out["pct_log_ge1_" + org] = share(logs, lambda v: v >= LOG_THRESHOLD)[0]
        out["pct_cfug_gt10_" + org], out["n_cfug_" + org] = share(cfu, lambda v: v > 10.0)
        out["n_cfug_zero_" + org] = sum(1 for v in cfu if v == 0.0)
        out["log_values_when_cfug_zero_" + org] = sorted(set(
            "missing" if rec["log10cfug_" + org] is None else rec["log10cfug_" + org]
            for rec in hh if rec["cfug_" + org] == 0.0), key=str)[:10]
        out["median_log_" + org] = median([v for v in logs if v is not None and v >= 0])
    # Row-level consistency of the lab columns.
    out["afla_out_of_range_rows"] = sum(
        1 for r in rows if num(r.get("aflatoxin")) is not None and not 0.0 <= r["aflatoxin"] <= CENSOR_PPB)
    for org in ORGANISMS:
        checked = mismatched = 0
        av_checked = av_mismatched = 0
        ratios = set()
        for r in rows:
            cfug, log = num(r.get("cfug_" + org)), num(r.get("log10cfug_" + org))
            if cfug is not None and cfug > 0:
                checked += 1
                if log is None or abs(math.log10(cfug) - log) > LOG_TOLERANCE:
                    mismatched += 1
            p1, p2, av = (num(r.get("plate1_" + org)), num(r.get("plate2_" + org)),
                          num(r.get("avecout_" + org)))
            if p1 is not None and p2 is not None and av is not None:
                av_checked += 1
                if abs(av - (p1 + p2) / 2.0) > AVERAGE_TOLERANCE:
                    av_mismatched += 1
            if av and cfug is not None:
                ratios.add(round(cfug / av, 3))
        out["log_checked_" + org], out["log_mismatched_" + org] = checked, mismatched
        out["avg_checked_" + org], out["avg_mismatched_" + org] = av_checked, av_mismatched
        out["cfug_per_average_count_" + org] = sorted(ratios)[:10]
    return out


def checks(c):
    """The 12 graded checks of docs/senegal-groundnut-0.1.0.md: list of dicts."""
    out = []

    def add(cid, claim, reported, computed, held):
        out.append({"id": cid, "claim": claim, "reported": reported, "computed": computed, "held": bool(held)})

    def pct(cid, claim, reported, key):
        add(cid, claim, reported, c[key], rounds_to(c[key], reported))

    add("S1", "250 households surveyed (households in the file, or households with consent = 1)", "250",
        [c["n_households"], c["n_consent1"]], c["n_households"] == 250 or c["n_consent1"] == 250)
    pct("S2", "% of producers who knew of aflatoxins (aflx_heard = 1)", "20", "pct_aflx_heard")
    pct("S3", "% who knew about bacterial contamination before the study (bac_heard = 1)", "22",
        "pct_bac_heard")
    pct("S4", "% of samples below the EU limit of 4 ppb (aflatoxin < 4)", "87", "pct_afla_lt4")
    pct("S5", "% of samples above 100 ppb (aflatoxin at the 100 ppb censoring value)", "8", "pct_afla_ge100")
    pct("S6", "% of samples with coliforms above 1 log CFU/g", "97", "pct_log_gt1_coli")
    pct("S7", "% of samples with Enterobacteriaceae above 1 log CFU/g", "94.5", "pct_log_gt1_eb")
    pct("S8", "% of households consuming raw groundnuts (prod_consall__1 = 1)", "7", "pct_prod_consall__1")
    add("S9", "every aflatoxin value lies in 0-100 ppb (censoring as documented)", "0",
        c["afla_out_of_range_rows"], c["afla_out_of_range_rows"] == 0 and c["n_aflatoxin"] > 0)
    mism = sum(c["log_mismatched_" + o] for o in ORGANISMS)
    chk = sum(c["log_checked_" + o] for o in ORGANISMS)
    add("S10", "log10 CFU/g columns equal log10 of the CFU/g columns (within 0.01) on every row with CFU/g > 0",
        "0", [mism, chk], mism == 0 and chk > 0)
    amism = sum(c["avg_mismatched_" + o] for o in ORGANISMS)
    achk = sum(c["avg_checked_" + o] for o in ORGANISMS)
    add("S11", "average colony count = mean of the two plates (within 0.5) on every row with both plates",
        "0", [amism, achk], amism == 0 and achk > 0)
    conf = sum(c["lab_conflicts"].values())
    add("S12", "no household has two different values of any lab result", "0", conf, conf == 0)
    return out


def predictions(results):
    held = {r["id"]: r["held"] for r in results}
    n_held = sum(1 for r in results if r["held"])
    return {
        "P1 S1 holds": held["S1"],
        "P2 at least 9 of 12 checks hold": n_held >= 9,
        "P3 S9-S12 all hold": all(held[k] for k in ("S9", "S10", "S11", "S12")),
        "P4 (guess) at least one of S4-S7 fails": not all(held[k] for k in ("S4", "S5", "S6", "S7")),
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
        req = urllib.request.Request(args.url, headers={"User-Agent": "senegal-groundnut-check/0.1.0 (mv2@munimtech.com)"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read()
        with open(os.path.join(args.out_dir, "hhfinal_share.tab"), "wb") as fh:
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
    path = os.path.join(args.out_dir, "senegal_groundnut_check.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1, sort_keys=True, default=str)
    for r in results:
        print("%-4s %-5s reported %-6s computed %s  %s" % (
            r["id"], "held" if r["held"] else "FAIL", r["reported"], r["computed"], r["claim"]))
    print(json.dumps(report["predictions"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
