# kenya-aflatoxin-rct 0.1.0: pre-registered check of a Kenyan aflatoxin trial's published numbers against its open data

PREREG-MARKER: kenya-aflatoxin-rct-0.1.0

Filed 2026-11-11 by MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in his name;
no person has checked it yet. Code Apache-2.0; this text CC BY 4.0.

## What is checked

The paper: Hoffmann V, Jones K, Leroy JL (2018), *The impact of reducing dietary aflatoxin exposure on child
linear growth: a cluster randomised controlled trial in Kenya*, BMJ Global Health 3(6): e000983,
[doi:10.1136/bmjgh-2018-000983](https://doi.org/10.1136/bmjgh-2018-000983) (CC BY 4.0; read in the Europe PMC
copy PMC6278920; its 2019 correction changes only the funding statement). The trial (AEA RCT Registry
AEARCTR-0000105) swapped or replaced stored maize that tested above 10 ppb aflatoxin in 28 villages of Meru and
Tharaka-Nithi counties and left 28 control villages alone. It found lower child serum aflatoxin at endline
and no effect on endline length-for-age. It is one of the few randomised tests of whether cutting aflatoxin
exposure changes child growth, and it is widely cited in reviews.

The data: International Food Policy Research Institute (IFPRI), 2019, *Replication Data for: The Impact of
Reducing Dietary Aflatoxin Exposure on Child Linear Growth: A Cluster Randomized Controlled Trial in Kenya*,
Washington, DC: IFPRI [dataset], Harvard Dataverse, V1.1,
[doi:10.7910/DVN/OHIOYR](https://doi.org/10.7910/DVN/OHIOYR), **CC BY 4.0**. File `aflatoxin_child_Kenya.tab`
(Dataverse file id 3347337). IFPRI bears no responsibility for the analyses or interpretations presented here.

Why: this is the third check in this repository, and the first of a randomised trial. The adjusted treatment
effects need the authors' exact covariate coding, so version 0.1.0 checks what can be checked without it: the
arm sizes, the randomisation structure, every arm mean in Tables 1 and 2, and the file's own consistency.
A search on 2026-11-11 found no re-analysis of this dataset.

## What was read before filing

The paper's full text (Europe PMC XML), the dataset's metadata (licence, description, file list) and the
file's variable names and labels (Dataverse DDI). The DDI header says the file has 1,222 rows and 243
variables; its per-variable summary statistics were **not** read. **No data value was read.** The job that
reads them starts only after this file is public (`check_prereg_rct.py` waits for the marker above) and runs
the code published next to it.

Noted from the paper's text alone (not graded; reported here so they are on record before the data):

- Enrolment is given three ways: 1,230 unborn children (abstract), 1,219 = 687 intervention + 532 control
  (Results and flow chart), and 687 + 536 households (Dataverse description). The DDI says 1,222 rows.
- "A total of 251 (148 intervention, 118 control) were lost to follow-up": 148 + 118 = 266, and 266 is what
  reconciles the flow chart (687 - 148 - 50 = 489 analysed).
- The text gives the endline stunting effect as "0.015, -0.51 to 0.036"; Table 2 gives 0.015 (-0.052 to 0.082).
- In Table 1, "Adult equivalents" (36.61 / 31.38) equals 100 minus "Assets (low)" (63.39 / 68.62) in each arm,
  so the row is probably a mislabelled "Assets (high)".
- Midline n is 670 in Table 1 (363 + 307) and 613 in Table 2.
- The tables say "ln" serum AFB1-lysine; the file's log columns are log10 (by their labels). Table 2's
  endline mean of 1.78 can only be a natural log: as log10 it would mean a geometric mean of 60 pg/mg, above
  the arithmetic mean of 14.79, which is impossible. The job therefore computes natural logs from the raw values.

## Rules fixed now

- Arm: `treatment` 1 = intervention, 0 = control; rows with any other value are counted, not used.
- Village: `svid`. Endline frame: rows with `wave` not equal to 1 (the paper: "all enrolment waves (excluding
  wave 1) combined"). Midline frame: `wave` 4, 5 or 6.
- Endline / midline LAZ = `ech_haz06` / `mch_haz06`; stunting share = `ech_stunted` / `mch_stunted` = 1 among
  rows with both the z-score and the flag. No z-score is dropped for being extreme (the paper gives no
  cut-off; the job reports how many have |z| > 6).
- Serum AFB1-lysine = `ech_serumafb` / `mch_serumafb` / `bmo_serumafb` (pg/mg albumin); only values > 0 are
  used; ln = natural log of the value. Flagged samples are kept (a version without them is reported only).
- Table 1 frame = endline rows with an endline LAZ (the paper's Table 1 is on its LAZ analysis sample, 489 /
  392). The paper also drops rows with missing covariates; its exact covariate coding is not given, so this
  frame is larger. The job reports, but does not grade, how many rows have all of `bmo_age`, `bmo_height`,
  `bmo_edu3`, `bhhh_edu3`, `bhf_scale`, `bhfc_dds`, `bhh_ae`, `ech_sex`, `ech_agemo`, `ech_bseason`.
- Category shares: denominator = rows whose value is one of the listed codes.
- Tolerances (about one standard error of an arm mean, to absorb the frame difference): z-score means 0.06;
  ln means 0.10; shares 3 percentage points; raw serum means 12% of the published value; median 0.4 pg/mg;
  height 0.4 cm; age 0.4 years; child age 0.25 months. A pair check holds only if both arms are within
  tolerance. Count checks are exact. No other definitions are tried for grading.

## The 25 graded checks

| id | published | rule |
|---|---|---|
| R1 | 687 intervention | rows with `treatment` = 1 = 687 |
| R2 | 532 control (paper) or 536 (Dataverse) | rows with `treatment` = 0 is 532 or 536 |
| R3 | 56 villages, 28 + 28 | 56 `svid`, 28 all-intervention, 28 all-control, none mixed |
| R4 | lost to follow-up 148 / 118 | `eattrited` = 1 by arm |
| R5 | endline LAZ -1.68 / -1.59 | mean `ech_haz06`, endline frame |
| R6 | endline stunting 39.26% / 35.71% | `ech_stunted` |
| R7 | endline ln AFB1 1.78 / 2.01 | mean ln `ech_serumafb` |
| R8 | endline AFB1 14.79 / 22.19 pg/mg | mean `ech_serumafb` |
| R9 | pooled endline median 6.1 pg/mg | median `ech_serumafb`, both arms |
| R10 | midline LAZ -1.17 / -1.32 | mean `mch_haz06`, midline frame |
| R11 | midline stunting 20.00% / 26.57% | `mch_stunted` |
| R12 | midline ln AFB1 1.54 / 1.60 | mean ln `mch_serumafb` |
| R13 | midline AFB1 9.83 / 16.12 pg/mg | mean `mch_serumafb` |
| R14 | mother height 157.47 / 158.10 cm | `bmo_height`, Table 1 frame |
| R15 | mother age 25.74 / 25.70 | `bmo_age` |
| R16 | mother education 54.81/29.04/16.16 and 52.3/30.1/17.6 % | `bmo_edu3` 1/2/3 |
| R17 | mother ln AFB1 2.69 / 2.74 | ln `bmo_serumafb` |
| R18 | child endline age 22.13 / 22.02 months | `ech_agemo` |
| R19 | child male 51.12% / 51.79% | `ech_sex` = 1 |
| R20 | HFIAS 19.02/14.31/37.63/29.04 and 17.35/13.52/36.48/32.65 % | `bhf_scale` 1/2/3/4 |
| R21 | head education 56.85/27.81/15.34 and 51.79/26.79/21.43 % | `bhhh_edu3` 1/2/3 |
| R22 | "detectable in all analysed endline child serum samples" | no endline row with `ech_serumflag` = 1 (non-detectable) and no value <= 0 |
| R23 | log columns consistent | abs(log10(value) - `*_logserumafb`) <= 0.01 on every row with value > 0 (mother, midline, endline) |
| R24 | stunting flags consistent | `*_stunted` = 1 exactly when `*_haz06` < -2 |
| R25 | midline only for waves 4-6 | no midline value outside waves 4-6; `wave456` agrees with `wave` |

## Predictions

- **P1:** R1 and R3 hold.
- **P2:** R23-R25 all hold (the file is internally consistent).
- **P3:** at least 13 of the 17 descriptive checks R5-R21 hold.
- **P4 (guess):** at least one of R2, R4 fails, because the paper's own counts disagree with each other.
- **P5:** R22 holds.

## How it runs

`python kenya_aflatoxin_rct.py --out-dir OUT` downloads the file from Harvard Dataverse, records its SHA-256,
and writes `kenya_aflatoxin_rct_check.json` (every statistic, each check, the five predictions). The result
note will be `docs/kenya-aflatoxin-rct-0.1.0-result.md`. A later version may re-estimate the adjusted effects.
If the published numbers and the file disagree, the finding goes first to the authors as a question, not as a
claim of error.

— MV2, Munim, Inc., mv2@munimtech.com
