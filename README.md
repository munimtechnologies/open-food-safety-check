# open-food-safety-check

Independent, pre-registered checks that published food-safety survey numbers can be re-computed from the
survey's own open data. By MV2 of Munim, Inc. (mv2@munimtech.com), made with AI agents working in his name.
Code Apache-2.0; text CC BY 4.0. Data stay with their publishers under their own licences and are
downloaded at run time, not stored here.

Each check is filed as a pre-registration (rules and predictions) **before** the data values are read; a
sealed job then waits until that file is public, runs the published code, and the result is written up
against the predictions, whatever they show. A disagreement is a question for the authors, not a verdict.
Anything looked at after grading is labelled post hoc and never changes a grade.

| check | survey | data | status |
|---|---|---|---|
| [kenya-aflatoxin 0.1.0](docs/kenya-aflatoxin-0.1.0.md) | Hoffmann et al. 2025, PLOS ONE 20(11): e0336687: aflatoxin in 1,255 maize-flour samples, ten Kenyan towns, 2021 | IFPRI, [doi:10.7910/DVN/XGNOD4](https://doi.org/10.7910/DVN/XGNOD4) (CC BY 4.0) | **graded 2026-11-13: 28 of 29 held** ([result](docs/kenya-aflatoxin-0.1.0-result.md)) |
| [senegal-groundnut 0.1.0](docs/senegal-groundnut-0.1.0.md) | Feed the Future Food Safety Innovation Lab (Purdue, ISRA) pilot: aflatoxins, coliforms and Enterobacteriaceae in groundnuts stored by 250 households, Peanut Basin, Senegal, 2020 | Bauchet 2021, [doi:10.7910/DVN/ACKHW5](https://doi.org/10.7910/DVN/ACKHW5) (CC0 1.0) | pre-registered 2026-11-11, 12 checks; job waiting for compute |
| [kenya-aflatoxin-rct 0.1.0](docs/kenya-aflatoxin-rct-0.1.0.md) | Hoffmann, Jones and Leroy 2018, BMJ Global Health 3(6): e000983: cluster randomised trial of aflatoxin-free maize and child growth, 56 villages, Meru and Tharaka-Nithi, 2013-2016 | IFPRI 2019, [doi:10.7910/DVN/OHIOYR](https://doi.org/10.7910/DVN/OHIOYR) (CC BY 4.0) | **graded 2026-11-13: 20 of 25 held** ([result](docs/kenya-aflatoxin-rct-0.1.0-result.md)); post hoc diagnostics added: the mother "log10" serum column holds the natural log in waves 4-6 |

The job outputs behind each graded result (every statistic, check and prediction) are in [results/](results/).
Post hoc diagnostic code is in [posthoc/](posthoc/). Every paper-and-data pair considered for a check,
including the ones not used and why, is listed in [docs/candidate-datasets.md](docs/candidate-datasets.md).

Run: `python -m unittest -v test_kenya_aflatoxin test_senegal_groundnut test_kenya_aflatoxin_rct`, then
`python kenya_aflatoxin.py --out-dir out`, `python senegal_groundnut.py --out-dir out` and
`python kenya_aflatoxin_rct.py --out-dir out` (Python 3.10+, standard library only). Post hoc: from
`posthoc/`, `python -m unittest -v test_posthoc_rct` then `python posthoc_rct.py --out-dir out`.

Related: 75 checked items in Canada's open food-chemistry data, in
[munimtechnologies/spice-lead-recalls](https://github.com/munimtechnologies/spice-lead-recalls).

IFPRI bears no responsibility for the analyses or interpretations of the data presented here.

— MV2, Munim, Inc., mv2@munimtech.com
