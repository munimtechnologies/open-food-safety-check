# senegal-groundnut 0.1.0: pre-registered check of a Senegal groundnut contamination pilot against its open data

PREREG-MARKER: senegal-groundnut-0.1.0

Filed 2026-11-11 by MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in his name;
no person has checked it yet. Code Apache-2.0; this text CC BY 4.0.

## What is checked

The published numbers: Yurani Arias-Granada (Purdue University), *Food for Thought: Contaminants in
Groundnut*, Feed the Future Innovation Lab for Food Safety (FSIL) program update,
<https://ag.purdue.edu/food-safety-innovation-lab/food-for-thought-contaminants-in-groundnut/> (dated
2020-06-01 on the page; it cites a 2021 paper, so it may have been posted later). It reports a pilot by
Purdue University and ISRA (Institut Sénégalais de Recherches Agricoles) that surveyed 250 smallholder
groundnut farmers in Senegal's Peanut Basin and tested their stored groundnuts for aflatoxins, coliforms,
Enterobacteriaceae and moulds. A summary of the same pilot also ran on Agrilinks ("How Safe are Groundnuts
Produced in Senegal? Main Takeaways from a Pilot Project").

The data: Bauchet, Jonathan, 2021, *Testing cost-effective interventions to reduce E. coli and other
contamination in Senegalese groundnut production and consumption*, Harvard Dataverse, V1.1,
[doi:10.7910/DVN/ACKHW5](https://doi.org/10.7910/DVN/ACKHW5), **CC0 1.0**. File `hhfinal_share.tab`
(Dataverse file id 4880423; "joined household survey and toxin lab results") and its dictionary
`hhfinal_share_dictionary.tab` (719 variables). The dataset lists no related publication.

Why: this is the second Global-South check in this repository (after
[kenya-aflatoxin 0.1.0](kenya-aflatoxin-0.1.0.md)), and the first one of microbial results and of a
programme summary rather than a journal paper. Programme summaries like this are what policy readers quote,
and they rarely carry their own denominators. A search on 2026-11-11 found no journal article giving these
numbers and no re-analysis of this dataset.

## What was read before filing

The FSIL post, the dataset's metadata (licence, file list, description) and the data dictionary (variable
names, types and labels). **No data value was read.** The job that reads them starts only after this file
is public (`check_prereg_senegal.py` waits for the marker above) and runs the code published next to it.

## Rules fixed now

- Unit = household = one `interview__key` (the dictionary also has a drying-method roster `dry__id`, so the
  file may hold several rows per household). A household's value of a variable = the first non-missing
  numeric value among its rows; households whose rows disagree on a lab result are counted (check S12).
- A share's denominator = households with a numeric value >= 0 for that variable (negative codes are
  treated as non-answers and counted separately). No weights. "Yes" = value 1.
- Aflatoxin (`aflatoxin`, ppb, "censored at 100 ppb"): "below the EU limit" = value < 4; "above 100 ppb" =
  value >= 100 (the censoring value). Coliforms / Enterobacteriaceae "above 1 log CFU/g" =
  `log10cfug_coli` / `log10cfug_eb` > 1. The `eb` suffix is read as Enterobacteriaceae (the dictionary
  does not spell it out).
- A published percentage holds if the computed value, rounded half-up to the decimals printed, equals it.
- No other definitions are tried for grading. Reported but not graded: <= 4 ppb, > 10 and > 20 ppb shares,
  >= 1 log, CFU/g > 10, raw-groundnut share over all households, medians, the smallest aflatoxin values,
  and what the log columns hold when CFU/g is 0.

## The 12 graded checks

| id | published / expected | variable and rule |
|---|---|---|
| S1 | 250 farmers surveyed | households in the file = 250, or households with `consent` = 1 = 250 |
| S2 | 20% knew of aflatoxins | `aflx_heard` = 1 |
| S3 | 22% knew about bacterial contamination before the study | `bac_heard` = 1 |
| S4 | 87% of samples below the EU limit (4 ppb) | `aflatoxin` < 4 |
| S5 | 8% of samples above 100 ppb | `aflatoxin` >= 100 |
| S6 | 97% of samples with coliforms above 1 log CFU/g | `log10cfug_coli` > 1 |
| S7 | 94.5% with Enterobacteriaceae above 1 log CFU/g | `log10cfug_eb` > 1 |
| S8 | 7% of households consume raw groundnuts | `prod_consall__1` = 1 |
| S9 | aflatoxin censored as documented | every `aflatoxin` value in 0-100 |
| S10 | log columns consistent | abs(log10(`cfug_x`) - `log10cfug_x`) <= 0.01 on every row with `cfug_x` > 0 (x = eb, coli, mold) |
| S11 | colony averages consistent | abs(`avecout_x` - mean of `plate1_x`, `plate2_x`) <= 0.5 on every row with both plates |
| S12 | one lab result per household | no household has two different values of any lab column |

## Predictions

- **P1:** S1 holds.
- **P2:** at least 9 of the 12 checks hold.
- **P3:** S9-S12 all hold (the file is internally consistent).
- **P4 (guess, low confidence):** at least one of S4-S7 fails at the printed precision, because the post
  may describe an earlier cut of the lab data than the file deposited in 2021 (V1.1 in 2024). If one fails,
  the result note gives the computed value and any simple definition change that reproduces it, labelled
  as found afterwards.

Not graded: "65% valued the technology at its current market price or above" (Aflasafe auction; the
"current market price" is not given in the post), and a 10% share above the US limit attributed to the same
work in a dissertation abstract that we could not open (the job reports the > 20 ppb share).

## How it runs

`python senegal_groundnut.py --out-dir OUT` downloads the file from Harvard Dataverse, records its SHA-256,
and writes `senegal_groundnut_check.json` (every statistic, each check, the four predictions). The result
note will be `docs/senegal-groundnut-0.1.0-result.md`. If the published numbers and the file disagree, the
finding goes first to the authors as a question, not as a claim of error.

— MV2, Munim, Inc., mv2@munimtech.com
