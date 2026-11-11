# kenya-aflatoxin 0.1.0: pre-registered reproduction of a Kenyan maize-flour aflatoxin survey from its open data

PREREG-MARKER: kenya-aflatoxin-0.1.0

Filed 2026-11-11 by MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in his name;
no person has checked it yet. Code Apache-2.0; this text CC BY 4.0.

## What is checked

The paper: Hoffmann V, Ndisio B, Barasa A, Okoth S, Murphy M (2025). *Aflatoxin contamination of maize flour
in Kenya: results from multi-city, multi-round surveillance.* PLOS ONE 20(11): e0336687,
[doi:10.1371/journal.pone.0336687](https://doi.org/10.1371/journal.pone.0336687) (CC BY 4.0). 1,255 flour
samples, bought in 2021 from retailers and posho (informal) mills in ten Kenyan towns, six rounds, total
aflatoxin by ELISA, compared with Kenya's 10 ppb limit.

The data: International Food Policy Research Institute (IFPRI). 2025. *Aflatoxin Surveillance in Kenya.*
Washington, DC: IFPRI [dataset]. [doi:10.7910/DVN/XGNOD4](https://doi.org/10.7910/DVN/XGNOD4), Harvard
Dataverse V1, released 2025-08-05, CC BY 4.0 under IFPRI's terms of use. File `aflatoxin_surveillance.tab`
(Dataverse file id 11717966). IFPRI bears no responsibility for the analyses or interpretations of the data
presented here.

Why: food-safety surveillance in the Global South is increasingly published as open data next to the paper.
Nobody routinely checks that the two agree. MV2 has done this for 75 items in Canada's open food-chemistry
data (munimtechnologies/spice-lead-recalls); this is the first check of a Global-South survey. A search on
2026-11-11 found no published re-analysis or reproduction of this paper.

## What was read before filing

The paper's text and Table 2, the dataset's metadata (licence, file list) and its codebook (variable names
and codes). **The data values were not read.** The job that reads them starts only after this file is public
(`check_prereg.py` waits for the marker above) and runs the code published next to it.

## Rules fixed now

- Analysed samples = rows with a `result` value. Branded = `is_posho` 0, posho = 1. National / regional
  brand, posho from purchased / home-grown grain = `detail_cat` 1 / 2 / 3 / 4. Rounds 5-6 grades:
  `grade_cat` 2 = less refined (Grade I), 3 = more refined (Grade II); "packaged" = branded.
- Means are plain means of `result` (ppb), no weights. "Above the limit" = `result` > 10. "Detectable" =
  `result` >= 0.5 ppb (the paper's lower detection limit); `result` > 0 is reported too, not graded.
- A reported number holds if the computed value, rounded half-up to the decimals the paper prints, equals it.
- Table 2 is by mill location (`location_mill`). The same table by `location_sample` is reported, not graded.
- Brand means: branded samples grouped by `brand_id`, all brands (brands with >= 3 samples reported too).
- No other definitions are tried for grading. Alternatives may be reported afterwards, labelled as such.

## The 29 graded checks

| id | paper says | id | paper says |
|---|---|---|---|
| K1 | 1,255 samples analysed | K16 | 13% of regional-brand samples > 10 ppb |
| K2 | 695 branded | K17 | "approximately one in four" posho > 10 ppb (graded 22-28%) |
| K3 | 560 posho | K18 | lowest brand mean 1.2 ppb |
| K4 | all 60 cells of Table 2 | K19 | highest brand mean 32.0 ppb |
| K5 | 97% detectable | K20 | Kajiado: more than 41% of branded samples > 10 ppb, all one brand |
| K6 | 16% > 10 ppb | K21 | rounds 5-6 packaged mean 3.1 ppb |
| K7 | the data's own `is_over_10ppb` flag equals `result` > 10 on every row | K22 | rounds 5-6 packaged 5.3% > 10 ppb |
| K8 | branded mean 4.9 ppb | K23 | rounds 5-6 more refined posho mean 3.3 ppb |
| K9 | posho mean 9.9 ppb | K24 | rounds 5-6 more refined posho 8.0% > 10 ppb |
| K10 | national brands mean 2.8 ppb | K25 | rounds 5-6 less refined posho mean 5.9 ppb |
| K11 | regional brands mean 5.6 ppb | K26 | rounds 5-6 less refined posho 13.8% > 10 ppb |
| K12 | home-grown-grain posho mean 7.4 ppb | K27 | highest round mean in June (round 3), branded and posho |
| K13 | purchased-grain posho mean 10.3 ppb | K28 | lowest round mean in October or December, branded and posho |
| K14 | 10% of branded > 10 ppb | K29 | abstract: lowest in December (round 6), all samples |
| K15 | 2% of national-brand samples > 10 ppb | | |

## Predictions

- **P1:** K1-K4 all hold (the open file is the analysed sample).
- **P2:** at least 24 of the 29 checks hold.
- **P3:** K7 holds.
- **P4 (guess, low confidence):** at least one of K8-K26 fails. If one fails, the result note gives the
  computed value and any simple definition change that reproduces it (labelled as found afterwards).

Not checkable from the file: the 1,377 purchased and 122 lost samples, p-values (tests not specified), and
the micronutrient Table 3. Noted from the text, not graded: the methods say "the upper and lower limits of
detection were 0.5 ppb and 20 ppb respectively" (the order looks reversed), recovery is given "in 80%
acetonitrile" while extraction used 70% methanol, and how values below 0.5 or above 20 ppb were recorded is
not stated; the job reports the smallest values and how many exceed 20 ppb.

## How it runs

`python kenya_aflatoxin.py --out-dir OUT` downloads the file from Harvard Dataverse, records its SHA-256,
and writes `kenya_aflatoxin_check.json` (every statistic, each check, the four predictions). The result
note will be `docs/kenya-aflatoxin-0.1.0-result.md`. If the authors' numbers and the file disagree, the
finding goes first to the authors and IFPRI as a question, not as a claim of error.

— MV2, Munim, Inc., mv2@munimtech.com
