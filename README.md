# open-food-safety-check

Independent, pre-registered checks that published food-safety survey numbers can be re-computed from the
survey's own open data. By MV2 of Munim, Inc. (mv2@munimtech.com), made with AI agents working in his name.
Code Apache-2.0; text CC BY 4.0. Data stay with their publishers under their own licences and are
downloaded at run time, not stored here.

Each check is filed as a pre-registration (rules and predictions) **before** the data values are read; a
sealed job then waits until that file is public, runs the published code, and the result is written up
against the predictions, whatever they show. A disagreement is a question for the authors, not a verdict.

| check | survey | data | status |
|---|---|---|---|
| [kenya-aflatoxin 0.1.0](docs/kenya-aflatoxin-0.1.0.md) | Hoffmann et al. 2025, PLOS ONE 20(11): e0336687: aflatoxin in 1,255 maize-flour samples, ten Kenyan towns, 2021 | IFPRI, [doi:10.7910/DVN/XGNOD4](https://doi.org/10.7910/DVN/XGNOD4) (CC BY 4.0) | pre-registered 2026-11-11, 29 checks |

Run: `python -m unittest -v test_kenya_aflatoxin` then `python kenya_aflatoxin.py --out-dir out`
(Python 3.10+, standard library only).

Related: 75 checked items in Canada's open food-chemistry data, in
[munimtechnologies/spice-lead-recalls](https://github.com/munimtechnologies/spice-lead-recalls).

IFPRI bears no responsibility for the analyses or interpretations of the data presented here.

— MV2, Munim, Inc., mv2@munimtech.com
