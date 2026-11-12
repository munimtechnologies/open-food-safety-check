# Candidate datasets for open-food-safety-check

Last updated: 2026-11-12 (third scouting pass: Zenodo and Dryad; later the same day, an anonymous download route
for the wheat DON paper's supplement). Text licence: CC BY 4.0.

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

## Parked: open licence and open paper, but the files cannot be downloaded by an automated job

On 2026-11-12 Dryad answered an anonymous request to its file-download API with HTTP 401, and its
website's file link returned HTTP 403 to an automated client. A second anonymous request later that day
(the README of doi:10.5061/dryad.d2547d8bx, file 4202051) again returned HTTP 401. Public reports of the
401 ("must have current bearer token") go back to at least August 2026. A Dryad API token is a
personal credential, and this repository's jobs run in sealed containers without credentials, so these pairs
are parked for now. Metadata and file lists are still public, so the entries below record what was confirmed
on 2026-11-12. A person could download the files in a browser and the job could then check them against the
sizes and SHA-256 digests that Dryad lists.

A partial route exists for papers in PubMed Central's open-access subset: PMC's Open Access dataset on AWS
(https://pmc-oa-opendata.s3.amazonaws.com/, no account needed) serves each article's full text and
supplementary files, and lists an MD5 for each file in a per-article JSON record (for example
PMC12506668.1/PMC12506668.1.json). It works when the PMC and publisher web pages refuse automated readers.
It only helps when the values a check needs are in the journal supplement, not in a separate Dryad deposit.

| Candidate | Notes (checked 2026-11-12) |
|---|---|
| Wheat deoxynivalenol (DON), genomic and hyperspectral prediction: Concepcion, Noble, Thompson, Dong, Olson 2025, G3 15(10) jkaf176, doi:10.1093/g3journal/jkaf176 (PMC12506668, CC BY); data doi:10.5061/dryad.d2547d8bx (CC0, version 379172, 110,287,108 bytes in five files: 2021_Phenomic_Data_VIS-NIR.csv, 2022_Phenomic_Data_VIS-NIR.csv, 2021-2022_Across_Years_Phenomic_Data_VIS-NIR.csv, a 3,117 x 15,456 imputed SNP matrix of 107,488,221 bytes, and a README) | The strongest candidate found so far. The paper can be read openly in Europe PMC, the data are CC0, and the prediction comparison (visible-band phenomic vs genomic vs blended models) is a published, checkable claim. The paper's data statement says the DON values are in Supplementary Tables 2 to 4 (BLUEs for the training genotypes), not on Dryad. That supplement is one zip file (jkaf176_supplementary_data.zip, 963,622 bytes; PMC lists MD5 943fda4e1996af4984f4ecc16f3202c1), and on 2026-11-12 it downloaded without login from PMC's Open Access dataset on AWS (path PMC12506668.1/). Its contents were not opened; a check would be pre-registered first. So the DON half is reachable by an automated job, but the genotype and spectral halves are still Dryad-only and blocked by the download rule above. |
| Maize yield and aflatoxin combining ability, southeastern USA: Knoll, Perla, Krakowsky, Guo 2023, Crop Science 63:2793-2806, doi:10.1002/csc2.21050 (Unpaywall: hybrid open access, CC BY); data doi:10.5061/dryad.ttdz08m44 (CC0; one .xlsx file, 354 KB, plus a README) | Two NC Design II experiments at Tifton, GA (18 lines x 6 testers; 13 lines x 10 testers); the abstract gives aflatoxin H2 = 0.09 and 0.27. Blocked by the Dryad download rule, and the Wiley article page returns HTTP 403 to automated readers. The USDA Ag Data Commons copy (figshare article 29937185) is only a link to the Dryad record. |
| Maize combining ability in expired-PVP lines and aflatoxin resistance: Knoll, Jeffers, Babiker 2026, Crop Science, doi:10.1002/csc2.70364 (Unpaywall: hybrid open access, public domain); data doi:10.5061/dryad.6djh9w1jc (CC0, about 430 KB) | 32 ex-PVP lines x 6 USDA-ARS lines in four environments. Same blockers as the 2023 pair (Dryad download rule; Wiley page not readable by tools). |

## Considered and not used

| Candidate | Why not (as of the date checked) |
|---|---|
| Guatemala PHLIL aflatoxin data, doi:10.7910/DVN/1WIY93 (and Phase 2, doi:10.7910/DVN/LSJC0Y, same project) | No open licence; the terms say distribution outside the platform is prohibited. |
| Ghana spectral kernel sorting, doi:10.7910/DVN/JSOG34 (Chavez et al. 2023, Food Control 151) | The paper is not open access, so its numbers cannot be checked openly. |
| Rwanda child aflatoxin and stunting, doi:10.17026/DANS-XVD-DZ6G (Uwiringiyimana; DANS) | Checked 2026-11-11: four of the five files are restricted (access by request) under the DANS Licence; the related work is a 2019 PhD thesis rather than a journal article. |
| Texas Feed & Fertilizer Control Service aflatoxin series 2022-2025 (Herrman; Texas Data Repository, e.g. doi:10.18738/T8/RIIXFE) | Checked 2026-11-11: the harvested record carries no licence, and the related paper (Lee, Herrman, Kim, Vasudevan 2026, Food Additives & Contaminants: Part A 43(4):615-642, doi:10.1080/19440049.2026.2632127) is not open access (Crossref lists only the publisher's text-and-data-mining policy). Parked; it could be reconsidered if a reuse licence is confirmed. |
| Winter wheat FHB and DON (ELISA vs FC-MS/MS): McConachie, Serajazari, Booker 2026, Canadian Journal of Plant Pathology 48(4):305-319, doi:10.1080/07060661.2026.2632743; data doi:10.5683/SP3/LHUPPG (Borealis) | Checked 2026-11-11: data CC BY 4.0 and open, but the paper is closed access (Unpaywall: closed), so its numbers cannot be checked openly. |
| RGB maize kernel images for aflatoxin and fumonisin detection (Kiwoli; doi:10.7910/DVN/IWAUTS) | Checked 2026-11-11: CC0 and open, but it is about 16 GB of images with no related publication, so there are no published numbers to check. It could suit a separate computer-vision baseline, not this repository. |
| Mycotoxins in plant-based meat alternatives: Mihalache, Torrijos, Dall'Asta 2024, Environment International article 108537, doi:10.1016/j.envint.2024.108537 (gold open access, CC BY); supplement doi:10.5281/zenodo.15565422 (CC BY 4.0) | Checked 2026-11-12: the Zenodo deposit holds seven .docx summary tables and figures, not sample-level data, so there is nothing to recompute independently. |
| "Aflatoxin in Ga Kenkey" (Dankyi, University of Ghana; doi:10.5281/zenodo.21497761; CC BY 4.0; one 15 KB .xlsx file) | Checked 2026-11-12: open, but the record has no description, codebook or linked publication, so there are no published numbers to check. Could be reconsidered if a paper appears. |
| HyperPistachio hyperspectral images of aflatoxin B1 contaminated pistachios (doi:10.5281/zenodo.20027441) | Checked 2026-11-12: CC BY-ND 4.0 with an "academic education and research purposes only" statement, and about 2.9 GB of images; not a paper-and-data check. |
| Aflatoxin Index (AFI) ensemble simulations for Euro-Mediterranean maize (doi:10.5281/zenodo.19597370; CC BY 4.0) | Checked 2026-11-12: model output (one NetCDF file) with no linked publication in the record; not a food-sample dataset. |

Searches behind this page:
- Harvard Dataverse dataset search for "aflatoxin", "fumonisin" and "mycotoxin" (the "mycotoxin" search
  returned 9 datasets on 2026-11-11; the ones not listed here are not about food or feed safety data, for
  example fish-health and wheat-nursery records).
- Zenodo dataset search (2026-11-12) for "aflatoxin" (25 most recent records read) and for
  "(fumonisin OR deoxynivalenol OR ochratoxin) AND maize" (1 hit, a bacterial genome assembly). Records
  not listed here are not food-safety data (for example a Poisson-solver benchmark, a vein-imaging set,
  electrochemical sensor raw data without a linked paper, and restricted or embargoed records).
- Dryad search (2026-11-12) for "aflatoxin" (6 datasets), "mycotoxin" (12) and "fumonisin" (0). Apart from
  the three parked pairs, the hits are about fungal population genetics and taxonomy, Drosophila mycotoxin
  tolerance, wheat head images, and DON effects in human cell lines.

No fourth check will be filed until the three pre-registered checks above have been graded.

Made with AI agents working in MV2's name; no person has reviewed this page yet.

— MV2, Munim, Inc., mv2@munimtech.com
