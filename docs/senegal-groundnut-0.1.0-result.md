# senegal-groundnut 0.1.0: result

RESULT-MARKER: senegal-groundnut-0.1.0-result

Graded 2026-11-15 by MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in his name; no person
has checked it yet. Code Apache-2.0; this text CC BY 4.0.

**5 of the 12 pre-registered checks held.** The survey numbers (250 farmers, 20% who knew of aflatoxins, 22% who
knew of bacterial contamination) and the 97% coliform share reproduce, and every log10 column matches its CFU/g
column. The two aflatoxin shares missed under the pre-registered household rule. Found after grading: the file
has **two aflatoxin samples for most households**, and counted per sample, as the post says ("In 87% of
groundnut samples"), **both reproduce exactly** (267 of 308 = 86.7%, and 25 of 308 = 8.1%). That reading is
post hoc and changes no grade. Still open: the 94.5% Enterobacteriaceae share (no count of the file's 184
samples prints as 94.5%), the 7% raw-consumption share (the file gives 7.6%), aflatoxin values coded 101 where
the codebook says censored at 100, and 5 colony averages that are not the mean of their two plates.

- Published numbers: Y. Arias-Granada, *Food for Thought: Contaminants in Groundnut*, Feed the Future Innovation
  Lab for Food Safety (Purdue University),
  <https://ag.purdue.edu/food-safety-innovation-lab/food-for-thought-contaminants-in-groundnut/>.
- Data: Bauchet, Jonathan, 2021, Harvard Dataverse V1.1, [doi:10.7910/DVN/ACKHW5](https://doi.org/10.7910/DVN/ACKHW5)
  (CC0 1.0), file `hhfinal_share.tab` (file id 4880423), 959,795 bytes, SHA-256
  `c7a8c385513f4429c0274bd92b9029a79d3c2578664549c94a7796aef6a713bb`; 677 rows, 719 columns.
- Pre-registration: [senegal-groundnut-0.1.0.md](senegal-groundnut-0.1.0.md) (public before the data were read; the
  job checked for its marker before downloading anything).
- Run: sealed job `senegal-groundnut-v1`, 2026-11-15 00:59 UTC, Python 3.12, standard library only. The unit tests
  passed first. The full output is
  [results/senegal_groundnut_check.json](../results/senegal_groundnut_check.json).

## Every check

A share holds when the computed value, rounded half-up to the decimals the post prints, equals the post's number.
Household value = the first non-missing value among the household's rows (the pre-registered rule).

| id | published | computed | held |
|---|---|---|---|
| S1 | 250 farmers surveyed | 250 households; 250 with consent = 1 | yes |
| S2 | 20% knew of aflatoxins | 50 of 250 = 20.00% | yes |
| S3 | 22% knew about bacterial contamination | 54 of 245 = 22.04% (5 households coded -888) | yes |
| S4 | 87% of samples below the EU limit (4 ppb) | 148 of 173 households = 85.55% | **no** |
| S5 | 8% of samples above 100 ppb | 17 of 173 households = 9.83% | **no** |
| S6 | 97% with coliforms above 1 log CFU/g | 178 of 184 = 96.74% | yes |
| S7 | 94.5% with Enterobacteriaceae above 1 log CFU/g | 175 of 184 = 95.11% | **no** |
| S8 | 7% of households consume raw groundnuts | 16 of 211 = 7.58% | **no** |
| S9 | every aflatoxin value in 0-100 ppb | 25 rows above 100 | **no** |
| S10 | log10 columns = log10 of the CFU/g columns | 0 of 537 differ | yes |
| S11 | colony average = mean of the two plates (within 0.5) | 5 of 552 differ | **no** |
| S12 | one value of each lab result per household | 129 households with two different aflatoxin values | **no** |

## The predictions, as filed

- **P1: S1 holds.** Held.
- **P2: at least 9 of the 12 checks hold.** Did not hold (5).
- **P3: S9-S12 all hold (the file is internally consistent).** Did not hold: S10 held; S9, S11 and S12 did not.
- **P4 (guess, low confidence): at least one of S4-S7 fails.** Held (S4, S5 and S7), but not for the reason the
  pre-registration guessed (an earlier cut of the lab data): S4 and S5 fail because of the unit, below.

## Reading the misses (found after grading, not pre-registered)

These counts were made directly in the deposited file after grading (the same file, same SHA-256). A script
that reproduces them, `posthoc/posthoc_senegal.py`, is queued in a sealed job and will be added with its output.

**The file has one row per sample, not per household.** Rows with `sample__id` 1 carry the microbial results;
rows with `sample__id` 2 and 3 carry one aflatoxin result each. 308 aflatoxin samples (163 with id 2, 145 with id
3) come from 173 households; 135 households have both samples, and in 129 of them the two values differ. The
pre-registration read the file as household rows and took the first aflatoxin value, so S4 and S5 used only one
sample per household, and S12 counted the two samples as a conflict. The microbial columns have no conflicts.
S12's miss is our misreading of the layout, not an inconsistency in the file.

**Counted per sample, the two aflatoxin shares reproduce:** below 4 ppb, 267 of 308 = 86.69%, which prints as
87%; above 100 ppb, 25 of 308 = 8.12%, which prints as 8%. (At or below 4 ppb it would be 270 of 308 = 87.66%.)

**S9: the censored values are coded 101.** All 25 values above 100 are exactly 101; none is exactly 100. The
codebook says "censored at 100 ppb", so 101 looks like a code for "above 100", not a measurement. Treated that
way it does not change S5.

**S7: 94.5% cannot come from 184 samples.** No count out of 184 prints as 94.5% (174 of 184 = 94.57%, 173 of 184
= 94.02%), so the post's figure used some other denominator. One of the file's 9 Enterobacteriaceae results at
or below 1 log is lab sample 160: plates 9 and 6, average recorded as 1.0 at dilution factor 1, giving 4 CFU/g
(0.60 log). Every other Enterobacteriaceae sample was read at dilution 10 or 100. With the plate mean (7.5) it
would be 30 CFU/g (1.48 log), and the share would be 176 of 184 = 95.65%, further from 94.5%.

**S11: the five averages that are not the plate mean** (lab sample numbers from `sampleno_labmicro`):

| lab sample | organism | plates | plate mean | recorded average |
|---|---|---|---|---|
| 160 | Enterobacteriaceae | 9, 6 | 7.5 | 1.0 |
| 128 | moulds | 44, 60 | 52.0 | 49.0 (the same as this sample's Enterobacteriaceae average) |
| 130 | moulds | 26, 27 | 26.5 | 52.0 |
| 127 | moulds | 50, 49 | 49.5 | 12.0 |
| 132 | moulds | 40, 35 | 37.5 | 26.5 |

The CFU/g and log columns follow the recorded average in each case, which is why S10 still holds. None of the
mould rows affects a published number (the post gives none for moulds).

**S8: the 7% needs a different denominator.** 16 households answered yes. Out of the 211 with an answer that is
7.58%; out of all 250 it is 6.40%. 16 yes answers print as 7% for any denominator from 214 to 246, so the post may
have used a slightly different base; we cannot tell which from the file.

## What this means

The survey answers and the coliform result reproduce as filed, and the two aflatoxin headline numbers reproduce
exactly once samples, not households, are counted, which is what the post says it counted. The pre-registration
got the file's layout wrong, and this note says so instead of re-grading. What remains are small points for the
authors, as questions, not claims of error: the denominator behind 94.5% and 7%, the 101 code, and five
colony averages.

— MV2, Munim, Inc., mv2@munimtech.com
