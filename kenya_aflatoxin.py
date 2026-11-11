# Apache-2.0. Copyright 2026 Munim, Inc. Made by MV2 of Munim, Inc. with AI agents.
"""kenya_aflatoxin 0.1.0: re-computes, from IFPRI's open data, the numbers reported in

  Hoffmann V, Ndisio B, Barasa A, Okoth S, Murphy M (2025). Aflatoxin contamination of maize flour in
  Kenya: results from multi-city, multi-round surveillance. PLOS ONE 20(11): e0336687.
  doi:10.1371/journal.pone.0336687 (CC BY 4.0)

  Data: International Food Policy Research Institute (IFPRI). 2025. Aflatoxin Surveillance in Kenya.
  Washington, DC: IFPRI [dataset]. doi:10.7910/DVN/XGNOD4, Harvard Dataverse, V1 (CC BY 4.0).
  IFPRI bears no responsibility for the analyses or interpretations of the data presented here.

and grades each reported number against the data, with the rules fixed in docs/kenya-aflatoxin-0.1.0.md
before the data were read. Standard library only.

  python kenya_aflatoxin.py --out-dir OUT [--tab-file PATH]   (no --tab-file: downloads DATA_URL)
"""
import argparse
import hashlib
import json
import os
import sys
import urllib.request
from decimal import ROUND_HALF_UP, Decimal

VERSION = "0.1.0"
DATA_URL = "https://dataverse.harvard.edu/api/access/datafile/11717966"
SITES = {1: "Eldoret", 2: "Kajiado", 3: "Kisumu", 4: "Machakos", 5: "Meru", 6: "Mombasa",
         7: "Nairobi", 8: "Nakuru", 9: "Nyeri", 10: "Thika"}
# Paper Table 2 (samples by mill location, all rounds):
# packaged all, national, regional, posho all, posho from purchased grain, posho from home-grown grain.
TABLE2 = {
    1: (95, 0, 95, 60, 55, 5),
    2: (17, 0, 17, 57, 30, 27),
    3: (47, 0, 47, 53, 41, 12),
    4: (48, 0, 48, 58, 48, 10),
    5: (66, 0, 66, 57, 53, 4),
    6: (53, 30, 23, 59, 54, 5),
    7: (138, 30, 108, 48, 48, 0),
    8: (45, 27, 18, 60, 55, 5),
    9: (33, 0, 33, 55, 50, 5),
    10: (153, 87, 66, 53, 49, 4),
}
COLUMNS = ("packaged_all", "national", "regional", "posho_all", "posho_purchased", "posho_homegrown")
MISSING = ("", ".", "NA", "NaN", "nan")
LOD = 0.5
THRESHOLD_PPB = 10.0


def parse_tab(text):
    """Rows of a Dataverse tab file (header line first) as dicts of name -> float or None."""
    lines = [ln for ln in text.splitlines() if ln.strip()]
    names = [h.strip().strip('"') for h in lines[0].split("\t")]
    rows = []
    for ln in lines[1:]:
        cells = [c.strip().strip('"') for c in ln.split("\t")]
        row = {}
        for i, name in enumerate(names):
            cell = cells[i] if i < len(cells) else ""
            row[name] = None if cell in MISSING else float(cell)
        rows.append(row)
    return rows


def rounds_to(value, reported):
    """True if value, rounded half-up to the decimals written in the string `reported`, equals it."""
    if value is None:
        return False
    places = len(reported.split(".")[1]) if "." in reported else 0
    quantum = Decimal(1).scaleb(-places)
    return Decimal(repr(float(value))).quantize(quantum, rounding=ROUND_HALF_UP) == Decimal(reported)


def mean(values):
    values = list(values)
    return sum(values) / len(values) if values else None


def pct(flags):
    flags = list(flags)
    return 100.0 * sum(1 for f in flags if f) / len(flags) if flags else None


def is_code(row, name, code):
    value = row.get(name)
    return value is not None and int(value) == code


def compute(all_rows):
    """Every statistic the checks need, from rows whose `result` is present (the analysed samples)."""
    rows = [r for r in all_rows if r.get("result") is not None]
    res = lambda rs: [r["result"] for r in rs]
    over = lambda rs: [r["result"] > THRESHOLD_PPB for r in rs]
    branded = [r for r in rows if is_code(r, "is_posho", 0)]
    posho = [r for r in rows if is_code(r, "is_posho", 1)]
    nat = [r for r in rows if is_code(r, "detail_cat", 1)]
    reg = [r for r in rows if is_code(r, "detail_cat", 2)]
    bought = [r for r in rows if is_code(r, "detail_cat", 3)]
    home = [r for r in rows if is_code(r, "detail_cat", 4)]
    late = [r for r in rows if r.get("round") is not None and int(r["round"]) in (5, 6)]
    out = {
        "n_rows": len(all_rows),
        "n_result_missing": len(all_rows) - len(rows),
        "n_analysed": len(rows),
        "n_branded": len(branded),
        "n_posho": len(posho),
        "pct_detectable": pct(r["result"] >= LOD for r in rows),
        "pct_above_zero": pct(r["result"] > 0 for r in rows),
        "pct_over_10": pct(over(rows)),
        "n_result_exactly_10": sum(1 for r in rows if r["result"] == THRESHOLD_PPB),
        "n_over_20": sum(1 for r in rows if r["result"] > 20),
        "min_result": min(res(rows)) if rows else None,
        "max_result": max(res(rows)) if rows else None,
        "n_below_lod": sum(1 for r in rows if r["result"] < LOD),
        "below_lod_values": sorted(set(r["result"] for r in rows if r["result"] < LOD))[:20],
        "flag_disagreements": sum(
            1 for r in rows if r.get("is_over_10ppb") is not None
            and (int(r["is_over_10ppb"]) == 1) != (r["result"] > THRESHOLD_PPB)),
        "flag_missing": sum(1 for r in rows if r.get("is_over_10ppb") is None),
        "mean_branded": mean(res(branded)),
        "mean_posho": mean(res(posho)),
        "mean_national": mean(res(nat)),
        "mean_regional": mean(res(reg)),
        "mean_homegrown": mean(res(home)),
        "mean_purchased": mean(res(bought)),
        "pct_over_branded": pct(over(branded)),
        "pct_over_national": pct(over(nat)),
        "pct_over_regional": pct(over(reg)),
        "pct_over_posho": pct(over(posho)),
    }
    # Table 2 by mill location (primary) and by sampling location (secondary, not graded).
    for key, loc in (("table2", "location_mill"), ("table2_by_sample_location", "location_sample")):
        table = {}
        for code in SITES:
            at = [r for r in rows if is_code(r, loc, code)]
            table[code] = (
                sum(1 for r in at if is_code(r, "is_posho", 0)),
                sum(1 for r in at if is_code(r, "detail_cat", 1)),
                sum(1 for r in at if is_code(r, "detail_cat", 2)),
                sum(1 for r in at if is_code(r, "is_posho", 1)),
                sum(1 for r in at if is_code(r, "detail_cat", 3)),
                sum(1 for r in at if is_code(r, "detail_cat", 4)),
            )
        out[key] = table
        out[key + "_n_no_location"] = sum(1 for r in rows if r.get(loc) is None)
    # Brand means (branded samples, grouped by brand_id).
    brands = {}
    for r in branded:
        if r.get("brand_id") is not None:
            brands.setdefault(int(r["brand_id"]), []).append(r["result"])
    brand_means = {b: mean(v) for b, v in brands.items()}
    out["n_brands"] = len(brand_means)
    out["brand_mean_min"] = min(brand_means.values()) if brand_means else None
    out["brand_mean_max"] = max(brand_means.values()) if brand_means else None
    multi = [m for b, m in brand_means.items() if len(brands[b]) >= 3]
    out["brand_mean_min_n3"] = min(multi) if multi else None
    out["brand_mean_max_n3"] = max(multi) if multi else None
    # Kajiado (mill location 2) branded samples.
    kaj = [r for r in branded if is_code(r, "location_mill", 2)]
    out["kajiado_branded_n"] = len(kaj)
    out["kajiado_branded_n_over"] = sum(1 for r in kaj if r["result"] > THRESHOLD_PPB)
    out["kajiado_branded_pct_over"] = pct(over(kaj))
    out["kajiado_branded_brands"] = sorted(set(int(r["brand_id"]) for r in kaj if r.get("brand_id") is not None))
    # Rounds 5-6 by refinement grade (grade_cat: 1 branded, 2 posho grade I less refined, 3 grade II more refined).
    for name, code in (("packaged", None), ("less_refined", 2), ("more_refined", 3)):
        if code is None:
            group = [r for r in late if is_code(r, "is_posho", 0)]
        else:
            group = [r for r in late if is_code(r, "grade_cat", code)]
        out["late_n_" + name] = len(group)
        out["late_mean_" + name] = mean(res(group))
        out["late_pct_over_" + name] = pct(over(group))
    # Round means.
    for name, group in (("branded", branded), ("posho", posho), ("all", rows)):
        by_round = {}
        for r in group:
            if r.get("round") is not None:
                by_round.setdefault(int(r["round"]), []).append(r["result"])
        out["round_means_" + name] = {k: mean(v) for k, v in sorted(by_round.items())}
    return out


def _argmax(d):
    return max(sorted(d), key=lambda k: d[k]) if d else None


def _argmin(d):
    return min(sorted(d), key=lambda k: d[k]) if d else None


def checks(c):
    """The 29 graded checks of docs/kenya-aflatoxin-0.1.0.md: list of (id, claim, reported, computed, held)."""
    out = []

    def add(cid, claim, reported, computed, held):
        out.append({"id": cid, "claim": claim, "reported": reported, "computed": computed, "held": bool(held)})

    def num(cid, claim, reported, key):
        add(cid, claim, reported, c[key], rounds_to(c[key], reported))

    add("K1", "samples analysed", "1255", c["n_analysed"], c["n_analysed"] == 1255)
    add("K2", "branded samples", "695", c["n_branded"], c["n_branded"] == 695)
    add("K3", "posho samples", "560", c["n_posho"], c["n_posho"] == 560)
    cells = sum(1 for code, row in TABLE2.items() for j in range(6) if c["table2"][code][j] == row[j])
    add("K4", "Table 2 cells by mill location (of 60)", "60", cells, cells == 60)
    num("K5", "% with detectable aflatoxin (>= 0.5 ppb)", "97", "pct_detectable")
    num("K6", "% above 10 ppb", "16", "pct_over_10")
    add("K7", "is_over_10ppb agrees with result > 10 on every row", "0", c["flag_disagreements"],
        c["flag_disagreements"] == 0 and c["flag_missing"] == 0)
    num("K8", "mean ppb, branded", "4.9", "mean_branded")
    num("K9", "mean ppb, posho", "9.9", "mean_posho")
    num("K10", "mean ppb, national brands", "2.8", "mean_national")
    num("K11", "mean ppb, regional brands", "5.6", "mean_regional")
    num("K12", "mean ppb, posho from home-grown grain", "7.4", "mean_homegrown")
    num("K13", "mean ppb, posho from purchased grain", "10.3", "mean_purchased")
    num("K14", "% above 10 ppb, branded", "10", "pct_over_branded")
    num("K15", "% above 10 ppb, national brands", "2", "pct_over_national")
    num("K16", "% above 10 ppb, regional brands", "13", "pct_over_regional")
    p = c["pct_over_posho"]
    add("K17", "% above 10 ppb, posho ('approximately one in four': 22-28%)", "22-28", p,
        p is not None and 22.0 <= p <= 28.0)
    num("K18", "lowest brand mean ppb", "1.2", "brand_mean_min")
    num("K19", "highest brand mean ppb", "32.0", "brand_mean_max")
    kp = c["kajiado_branded_pct_over"]
    add("K20", "Kajiado branded: more than 41% above 10 ppb, all one brand", ">41, 1 brand",
        [kp, c["kajiado_branded_brands"]], kp is not None and kp > 41.0 and len(c["kajiado_branded_brands"]) == 1)
    num("K21", "rounds 5-6 mean ppb, packaged", "3.1", "late_mean_packaged")
    num("K22", "rounds 5-6 % above 10 ppb, packaged", "5.3", "late_pct_over_packaged")
    num("K23", "rounds 5-6 mean ppb, more refined posho", "3.3", "late_mean_more_refined")
    num("K24", "rounds 5-6 % above 10 ppb, more refined posho", "8.0", "late_pct_over_more_refined")
    num("K25", "rounds 5-6 mean ppb, less refined posho", "5.9", "late_mean_less_refined")
    num("K26", "rounds 5-6 % above 10 ppb, less refined posho", "13.8", "late_pct_over_less_refined")
    peaks = [_argmax(c["round_means_branded"]), _argmax(c["round_means_posho"])]
    add("K27", "highest round mean is June (round 3) for branded and for posho", "3, 3", peaks,
        peaks == [3, 3])
    lows = [_argmin(c["round_means_branded"]), _argmin(c["round_means_posho"])]
    add("K28", "lowest round mean is October or December (round 5 or 6) for branded and for posho",
        "5|6, 5|6", lows, all(x in (5, 6) for x in lows))
    low_all = _argmin(c["round_means_all"])
    add("K29", "abstract: lowest in December (round 6), all samples pooled", "6", low_all, low_all == 6)
    return out


def predictions(results):
    held = {r["id"]: r["held"] for r in results}
    n_held = sum(1 for r in results if r["held"])
    reproduced = [r for r in results if r["id"] in ["K%d" % i for i in range(8, 27)]]
    return {
        "P1 counts K1-K4 all hold": all(held[k] for k in ("K1", "K2", "K3", "K4")),
        "P2 at least 24 of 29 checks hold": n_held >= 24,
        "P3 K7 holds": held["K7"],
        "P4 (guess) at least one of K8-K26 fails": any(not r["held"] for r in reproduced),
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
        req = urllib.request.Request(args.url, headers={"User-Agent": "kenya-aflatoxin-check/0.1.0 (mv2@munimtech.com)"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read()
        with open(os.path.join(args.out_dir, "aflatoxin_surveillance.tab"), "wb") as fh:
            fh.write(raw)
    rows = parse_tab(raw.decode("utf-8-sig"))
    stats = compute(rows)
    results = checks(stats)
    report = {
        "version": VERSION,
        "source_url": None if args.tab_file else args.url,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "columns": sorted(rows[0]) if rows else [],
        "stats": stats,
        "checks": results,
        "predictions": predictions(results),
    }
    path = os.path.join(args.out_dir, "kenya_aflatoxin_check.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1, sort_keys=True, default=str)
    for r in results:
        print("%-4s %-5s reported %-12s computed %s  %s" % (
            r["id"], "held" if r["held"] else "FAIL", r["reported"], r["computed"], r["claim"]))
    print(json.dumps(report["predictions"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
