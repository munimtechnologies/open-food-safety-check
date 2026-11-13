# kenya-aflatoxin-rct 0.1.0: result

RESULT-MARKER: kenya-aflatoxin-rct-0.1.0-result

Graded 2026-11-13 by MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in his name; no person
has checked it yet. Code Apache-2.0; this text CC BY 4.0. IFPRI bears no responsibility for the analyses or
interpretations of the data presented here.

**20 of the 25 pre-registered checks held, including 16 of the 17 arm means from Tables 1 and 2.** The trial's
open file reproduces the randomisation (56 villages, 28 per arm, none mixed), the loss to follow-up, and the
endline and midline growth and serum-aflatoxin means. The five misses are: two arm counts that differ from the
paper by one and two children, one Table 1 mean just outside its tolerance, 17 endline serum samples that the
file flags as non-detectable, and a mother serum "log10" column whose values do not match log10 of the serum
values on 885 of 1,206 rows.

- Paper: Hoffmann V, Jones K, Leroy JL (2018), BMJ Global Health 3(6): e000983,
  [doi:10.1136/bmjgh-2018-000983](https://doi.org/10.1136/bmjgh-2018-000983).
- Data: IFPRI 2019, Replication Data, Harvard Dataverse V1.1,
  [doi:10.7910/DVN/OHIOYR](https://doi.org/10.7910/DVN/OHIOYR) (CC BY 4.0), file `aflatoxin_child_Kenya.tab`,
  1,700,478 bytes, SHA-256 `d48ac94dc165930f2ec2dff546b31b9abc70ee28155a767ffe781a3b0504defe`, 1,222 rows,
  243 columns.
- Pre-registration: [kenya-aflatoxin-rct-0.1.0.md](kenya-aflatoxin-rct-0.1.0.md) (public before the data were
  read; the job checked for its marker before downloading anything).
- Run: sealed job `kenya-aflatoxin-rct-v1`, 2026-11-13 16:01-16:09 UTC, Python 3.12, standard library only.
  The 11 unit tests passed first. Full output:
  [results/kenya_aflatoxin_rct_check.json](../results/kenya_aflatoxin_rct_check.json).

## Every check

Pairs are intervention / control. A pair holds only if both arms are within the pre-registered tolerance.

| id | paper | computed | held |
|---|---|---|---|
| R1 | 687 intervention children | 688 | **no** |
| R2 | 532 control (paper) or 536 (Dataverse description) | 534 | **no** |
| R3 | 56 villages, 28 + 28, none mixed | 56, 28 + 28, 0 mixed | yes |
| R4 | lost to follow-up 148 / 118 | 148 / 118 | yes |
| R5 | endline LAZ -1.68 / -1.59 (0.06) | -1.69 / -1.60 | yes |
| R6 | endline stunting 39.26% / 35.71% (3 points) | 39.92% / 35.35% | yes |
| R7 | endline ln AFB1-lysine 1.78 / 2.01 (0.10) | 1.78 / 2.02 | yes |
| R8 | endline AFB1-lysine 14.79 / 22.19 pg/mg (12%) | 14.56 / 21.55 | yes |
| R9 | pooled endline median 6.1 pg/mg (0.4) | 6.19 | yes |
| R10 | midline LAZ -1.17 / -1.32 (0.06) | -1.22 / -1.32 | yes |
| R11 | midline stunting 20.00% / 26.57% (3 points) | 21.45% / 26.35% | yes |
| R12 | midline ln AFB1-lysine 1.54 / 1.60 (0.10) | 1.54 / 1.66 | yes |
| R13 | midline AFB1-lysine 9.83 / 16.12 pg/mg (12%) | 10.02 / 16.69 | yes |
| R14 | mother height 157.47 / 158.10 cm (0.4) | 157.15 / 158.63 | **no** |
| R15 | mother age 25.74 / 25.70 (0.4) | 25.49 / 25.54 | yes |
| R16 | mother education 54.81/29.04/16.16 and 52.3/30.1/17.6 % | 53.97/29.79/16.25 and 51.23/30.15/18.63 | yes |
| R17 | mother ln AFB1-lysine 2.69 / 2.74 (0.10) | 2.62 / 2.66 | yes |
| R18 | child endline age 22.13 / 22.02 months (0.25) | 22.13 / 22.09 | yes |
| R19 | child male 51.12% / 51.79% | 50.85% / 51.57% | yes |
| R20 | HFIAS 19.02/14.31/37.63/29.04 and 17.35/13.52/36.48/32.65 % | 18.98/13.85/37.38/29.79 and 17.96/13.35/36.41/32.28 | yes |
| R21 | head education 56.85/27.81/15.34 and 51.79/26.79/21.43 % | 57.33/27.43/15.24 and 51.96/26.96/21.08 | yes |
| R22 | "detectable in all analysed endline child serum samples" | 17 endline rows flagged non-detectable; 0 values <= 0 among 860 | **no** |
| R23 | log10 columns equal log10 of the serum values (0.01) | 885 of 2,709 differ, all in the mother column | **no** |
| R24 | stunted flag = (LAZ < -2) | 0 of 1,646 differ | yes |
| R25 | midline only in waves 4-6; `wave456` agrees | 0, 0 | yes |

## The predictions, as filed

- **P1: R1 and R3 hold.** Did not hold: R3 held, R1 is off by one (688, not 687).
- **P2: R23-R25 all hold.** Did not hold: R24 and R25 held, R23 failed.
- **P3: at least 13 of the 17 descriptive checks R5-R21 hold.** Held (16 of 17).
- **P4 (guess): at least one of R2, R4 fails.** Held: R2 failed. R4 held exactly, which settles one of the
  paper's inconsistencies noted before the data: the file's 148 + 118 = 266 losses fit the flow chart, so the
  text's "A total of 251" is the slip.
- **P5: R22 holds.** Did not hold.

## Reading the misses (found after grading, not pre-registered)

These use the output above and the dataset's own codebook (Dataverse DDI), read after grading.

- **R1, R2 (arm counts).** The codebook also counts 688 intervention and 534 control rows (1,222). The paper
  gives 687 + 532 = 1,219 children, and the dataset description 687 + 536 households. Three rows in the file
  are not in the paper's count; which ones is not yet known.
- **R14 (mother height).** Intervention is 0.32 cm from the paper, control 0.53 cm (tolerance 0.4). The
  pre-registration warned that its Table 1 frame (endline rows with a length-for-age score: 531 / 413) is larger
  than the paper's (489 / 392, after dropping rows with missing covariates whose coding the paper does not give).
  The frame difference is the likely reason, but this has not been shown.
- **R22 (non-detectable samples).** The codebook defines `ech_serumflag` 1 = "Non-detectable" (17 rows), 2 =
  "Insufficient volume (<150 ul)" (4) and 3 = "Hemolysis" (1). All 860 endline serum values in the file are
  positive (the smallest is 0.405 pg/mg). Only 4 of the 22 flagged endline rows have a serum value, so at least
  13 of the 17 non-detectable samples have no value in the file: they seem to have been left out, not set to a
  value below the detection limit. That is consistent with "all analysed samples" if analysed means "with a
  value". The pre-registered rule counted the flags, so the check fails as written. Which arm the
  non-detectable samples are in matters (dropping them raises that arm's mean), and is not yet known.
- **R23 (mother log column).** The child columns `ech_logserumafb` and `mch_logserumafb` equal log10 of the
  serum values on every row (860 and 643). The mother column `bmo_logserumafb` differs on 885 of 1,206 rows. Its
  codebook label is "Mother: log10 of mo_serumafb", but the codebook's own summary statistics give it a minimum
  of -1.4496 and a maximum of 7.2363, which are the **natural** logs of the mother serum minimum (0.2347) and
  maximum (1388.91); their log10 would be -0.630 and 3.143. Because 321 rows do agree with log10, the column
  may mix the two; that is not yet shown. This does not touch the paper's Table 1, which reports "ln" for
  mothers, and R17 (computed as the natural log of the raw values) held. It matters for anyone who reuses the
  column as labelled.

A short post hoc diagnostic job (`posthoc_rct.py`, labelled as post hoc and not changing any grade) is queued
to settle the open points: which log each mother row holds, the non-detectable samples by arm, the three extra
rows, and the mother-height miss under narrower frames. Its output will be added here.

## What this means

The open data back the trial's published arm means and its randomisation closely. The misses are bookkeeping:
small count differences, one Table 1 mean at the edge of tolerance, undocumented handling of non-detectable
samples, and one mislabelled or mixed derived column. None of this was checked against the paper's adjusted
treatment effects, which need the authors' covariate coding. The points will go to IFPRI and the authors as
questions, not as claims of error.

— MV2, Munim, Inc., mv2@munimtech.com
