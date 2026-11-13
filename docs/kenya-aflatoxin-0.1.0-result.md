# kenya-aflatoxin 0.1.0: result

RESULT-MARKER: kenya-aflatoxin-0.1.0-result

Graded 2026-11-13 by MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in his name; no person
has checked it yet. Code Apache-2.0; this text CC BY 4.0. IFPRI bears no responsibility for the analyses or
interpretations of the data presented here.

**28 of the 29 pre-registered checks held.** The open file reproduces the paper's sample counts, all 60 cells
of Table 2, every mean and every share above Kenya's 10 ppb limit. The one miss is the headline share of
samples with detectable aflatoxin: 94% at the paper's stated 0.5 ppb detection limit, against 97% in the paper.

- Paper: Hoffmann, Ndisio, Barasa, Okoth, Murphy (2025), PLOS ONE 20(11): e0336687,
  [doi:10.1371/journal.pone.0336687](https://doi.org/10.1371/journal.pone.0336687).
- Data: IFPRI 2025, *Aflatoxin Surveillance in Kenya*, Harvard Dataverse V1,
  [doi:10.7910/DVN/XGNOD4](https://doi.org/10.7910/DVN/XGNOD4) (CC BY 4.0), file `aflatoxin_surveillance.tab`,
  51,644 bytes, SHA-256 `3d6dc864040d715d313d5400801709b31b68c869895a56487cce5aa5c0871ada`.
- Pre-registration: [kenya-aflatoxin-0.1.0.md](kenya-aflatoxin-0.1.0.md) (public before the data were read; the
  job checked for its marker before downloading anything).
- Run: sealed job `kenya-aflatoxin-v1`, 2026-11-13 ~18:00 UTC, Python 3.12, standard library only. The 10 unit
  tests passed first. The full output is [results/kenya_aflatoxin_check.json](../results/kenya_aflatoxin_check.json).

## Every check

A check holds when the computed value, rounded half-up to the decimals the paper prints, equals the paper's number.

| id | paper | computed | held |
|---|---|---|---|
| K1 | 1,255 samples analysed | 1,255 | yes |
| K2 | 695 branded | 695 | yes |
| K3 | 560 posho | 560 | yes |
| K4 | all 60 cells of Table 2 (by mill location) | 60 of 60 | yes |
| K5 | 97% detectable (>= 0.5 ppb) | 94.42% | **no** |
| K6 | 16% above 10 ppb | 16.02% | yes |
| K7 | `is_over_10ppb` equals `result` > 10 on every row | 0 disagreements | yes |
| K8 | branded mean 4.9 ppb | 4.87 | yes |
| K9 | posho mean 9.9 ppb | 9.87 | yes |
| K10 | national brands mean 2.8 ppb | 2.76 | yes |
| K11 | regional brands mean 5.6 ppb | 5.58 | yes |
| K12 | posho from home-grown grain mean 7.4 ppb | 7.42 | yes |
| K13 | posho from purchased grain mean 10.3 ppb | 10.26 | yes |
| K14 | 10% of branded above 10 ppb | 10.07% | yes |
| K15 | 2% of national-brand samples above 10 ppb | 2.30% | yes |
| K16 | 13% of regional-brand samples above 10 ppb | 12.67% | yes |
| K17 | "approximately one in four" posho above 10 ppb (graded 22-28%) | 23.39% | yes |
| K18 | lowest brand mean 1.2 ppb | 1.20 | yes |
| K19 | highest brand mean 32.0 ppb | 32.03 | yes |
| K20 | Kajiado: more than 41% of branded above 10 ppb, all one brand | 7 of 17 = 41.18%, one brand | yes |
| K21 | rounds 5-6 packaged mean 3.1 ppb | 3.13 | yes |
| K22 | rounds 5-6 packaged 5.3% above 10 ppb | 5.33% | yes |
| K23 | rounds 5-6 more refined posho mean 3.3 ppb | 3.33 | yes |
| K24 | rounds 5-6 more refined posho 8.0% above 10 ppb | 8.05% | yes |
| K25 | rounds 5-6 less refined posho mean 5.9 ppb | 5.95 | yes |
| K26 | rounds 5-6 less refined posho 13.8% above 10 ppb | 13.76% | yes |
| K27 | highest round mean in June (round 3), branded and posho | round 3, round 3 | yes |
| K28 | lowest round mean in October or December, branded and posho | round 6, round 6 | yes |
| K29 | abstract: lowest in December (round 6), all samples | round 6 | yes |

## The predictions, as filed

- **P1: K1-K4 all hold.** Held.
- **P2: at least 24 of the 29 checks hold.** Held (28).
- **P3: K7 holds.** Held.
- **P4 (guess, low confidence): at least one of K8-K26 fails.** Did not hold: all 19 held.

## Reading the miss (found after grading, not pre-registered)

The pre-registration fixed "detectable" as `result` >= 0.5 ppb, the lower detection limit the methods give,
and also asked the job to report the share with `result` > 0 without grading it. That share is
**1,217 of 1,255 = 96.97%, which rounds to the paper's 97%.** At >= 0.5 ppb it is 1,185 of 1,255 = 94.42%.
The difference is 32 samples recorded with a value above 0 but below 0.5 ppb (the smallest is 0.024 ppb);
38 more are recorded as 0. So the 97% looks like the share of samples with any non-zero reading, not the share
at or above the stated detection limit. This is one reading that fits; the paper does not say how readings
below 0.5 ppb were treated, and the authors may have had a reason to count them.

Also seen in the output, not graded:

- The file has 1,377 rows, 122 of them without a result. That matches the paper's 1,377 samples purchased and
  122 lost, which the pre-registration had listed as not checkable.
- 111 samples are above 20 ppb (the largest is 166 ppb), although the methods give 20 ppb as a detection limit
  (in the order "upper and lower limits ... 0.5 ppb and 20 ppb", which looks reversed). High samples were
  probably diluted and re-read, but the paper does not say so.
- Grouping Table 2 by where the sample was bought (`location_sample`) instead of where it was milled gives
  different town counts; the paper's table matches the mill location, as the pre-registration assumed.

## What this means

This is a well-documented open dataset: everything the paper reports that can be recomputed from the file was
recomputed, except one headline share, and that share is reproduced exactly by a nearby definition. The point
will go to the authors and IFPRI as a question about how readings below 0.5 ppb were counted, not as a claim
of error.

— MV2, Munim, Inc., mv2@munimtech.com
