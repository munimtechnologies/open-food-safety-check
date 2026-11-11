# Candidate datasets for open-food-safety-check

Last updated: 2026-11-11 (second scouting pass). Text licence: CC BY 4.0.

This page lists every paper-and-data pair considered for a check in this repository, including the
ones that were not used and why. A check is only run when (1) the data are openly downloadable without
an access request, (2) the data licence allows reuse and redistribution of derived results (CC BY or CC0),
and (3) the paper whose numbers are checked can be read openly. Each check is pre-registered from the
paper and the codebook before any data values are read.

## Used (pre-registered)

| Check | Paper | Data | Licence | Status |
|---|---|---|---|---|
| kenya-aflatoxin 0.1.0 | Hoffmann, Ndisio, Barasa, Okoth, Murphy 2025, PLOS ONE 20(11) e0336687 | IFPRI, doi:10.7910/DVN/XGNOD4 | CC BY 4.0 | pre-registered, job queued |
| senegal-groundnut 0.1.0 | Feed the Future Innovation Lab for Food Safety post (Purdue) | Bauchet et al., doi:10.7910/DVN/ACKHW5 | CC0 | pre-registered, job queued |
| kenya-aflatoxin-rct 0.1.0 | Hoffmann, Jones, Leroy 2018, BMJ Global Health 3(6) e000983 | IFPRI, doi:10.7910/DVN/OHIOYR | CC BY 4.0 | pre-registered, job queued |

## Shortlisted (no check until the three above are graded)

| Candidate | Notes (as of the date checked) |
|---|---|
| Ghana Middle Belt maize markets: Danso, Osekre, Opit, Manu, Armstrong, Arthur, Campbell, Mbata, McNeill 2018, Journal of Stored Products Research 77:9-15, doi:10.1016/j.jspr.2018.02.004; data Opit, doi:10.7910/DVN/RJRQBH (one .xlsx file, 462 KB) | Checked 2026-11-11: data CC0, unrestricted, no guestbook. The paper is free to read as the publisher-hosted accepted manuscript (Unpaywall: bronze, no licence), but the publisher page refuses automated reading, so a pre-registration would need a person to read it or a copy that tools can open. |
| Ghana Middle Belt maize at harvest and post-harvest: Danso et al. 2017, Journal of Stored Products Research 74:46-55, doi:10.1016/j.jspr.2017.08.007; data Opit, doi:10.7910/DVN/BN2PMN (one .xlsx file, 184 KB) | Checked 2026-11-11: same situation as the 2018 pair (data CC0 and open; paper free to read as an accepted manuscript without a licence; not readable by automated tools). |

## Considered and not used

| Candidate | Why not (as of the date checked) |
|---|---|
| Guatemala PHLIL aflatoxin data, doi:10.7910/DVN/1WIY93 (and Phase 2, doi:10.7910/DVN/LSJC0Y, same project) | No open licence; the terms say distribution outside the platform is prohibited. |
| Ghana spectral kernel sorting, doi:10.7910/DVN/JSOG34 (Chavez et al. 2023, Food Control 151) | The paper is not open access, so its numbers cannot be checked openly. |
| Rwanda child aflatoxin and stunting, doi:10.17026/DANS-XVD-DZ6G (Uwiringiyimana; DANS) | Checked 2026-11-11: four of the five files are restricted (access by request) under the DANS Licence; the related work is a 2019 PhD thesis rather than a journal article. |
| Texas Feed & Fertilizer Control Service aflatoxin series 2022-2025 (Herrman; Texas Data Repository, e.g. doi:10.18738/T8/RIIXFE) | Checked 2026-11-11: the harvested record carries no licence, and the related paper (Lee, Herrman, Kim, Vasudevan 2026, Food Additives & Contaminants: Part A 43(4):615-642, doi:10.1080/19440049.2026.2632127) is not open access (Crossref lists only the publisher's text-and-data-mining policy). Parked; it could be reconsidered if a reuse licence is confirmed. |
| Winter wheat FHB and DON (ELISA vs FC-MS/MS): McConachie, Serajazari, Booker 2026, Canadian Journal of Plant Pathology 48(4):305-319, doi:10.1080/07060661.2026.2632743; data doi:10.5683/SP3/LHUPPG (Borealis) | Checked 2026-11-11: data CC BY 4.0 and open, but the paper is closed access (Unpaywall: closed), so its numbers cannot be checked openly. |
| RGB maize kernel images for aflatoxin and fumonisin detection (Kiwoli; doi:10.7910/DVN/IWAUTS) | Checked 2026-11-11: CC0 and open, but it is about 16 GB of images with no related publication, so there are no published numbers to check. It could suit a separate computer-vision baseline, not this repository. |

Searches behind this page: Harvard Dataverse dataset search for "aflatoxin", "fumonisin" and "mycotoxin"
(the "mycotoxin" search returned 9 datasets on 2026-11-11; the ones not listed here are not about food or
feed safety data, for example fish-health and wheat-nursery records).

No fourth check will be filed until the three pre-registered checks above have been graded.

Made with AI agents working in MV2's name; no person has reviewed this page yet.

— MV2, Munim, Inc., mv2@munimtech.com
