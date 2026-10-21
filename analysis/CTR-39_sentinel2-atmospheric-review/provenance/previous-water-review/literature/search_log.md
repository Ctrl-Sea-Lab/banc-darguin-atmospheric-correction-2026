# CTR-39 search record

Search date: 20 October 2026. Investigator: Rachel Carson. Review type: targeted critical review, not a systematic review.

Question: Which atmospheric corrections can be applied to Sentinel-2 marine ecology, and under which coastal optical conditions and application endpoints are comparisons informative?

Sources actually consulted: publisher pages/PDFs (Elsevier, MDPI, Optica, IEEE, Frontiers); Crossref public DOI metadata API; OpenAlex public works API for open-access locations; NASA NTRS; Plymouth Marine Laboratory repository; VLIZ; DLR; HAL; Ghent University repository; UConn institutional hosting; University of Maine educational hosting; ESA STEP/C2RCC documentation; author/developer sites. Search results from aggregators were discovery leads; scientific conclusions were checked against original publications. No Google Scholar, Semantic Scholar API, or subscription access was used.

## Discovery query strings

The following queries were run through the web search tool on the search date. They represent a targeted sequence expanded in response to results rather than a pre-registered database search.

1. `Sentinel-2 atmospheric correction coastal waters ACIX Aqua intercomparison Warren 2019 2023`
2. `Sentinel-2 atmospheric correction ACOLITE C2RCC iCOR Polymer marine coastal waters comparison 2024 2025 2026`
3. `Vanhellemont 2019 Adaptation dark spectrum fitting atmospheric correction Sentinel-2 111414`
4. `De Keukelaere 2018 iCOR atmospheric correction Sentinel-2 adjacency SIMEC`
5. `Steinmetz Deschamps Ramon 2011 atmospheric correction sun glint Polymer`
6. `Sentinel-2 atmospheric correction 2025 2026 coastal validation TSDSF RAdCor ACIX`
7. `Sentinel 2 atmospheric correction Warren 2019 assessment 03.018 full text`
8. `OC-SMART multi sensor ocean color atmospheric correction Fan 2021 Sentinel 2`
9. `C2RCC Brockmann 2016 evolution neural network atmospheric correction Sentinel 2`
10. `Vanhellemont Ruddick 2025 generalized physics based correction adjacency RAdCor DOI`
11. `Sentinel-2 Sen2Cor Main-Knorn 2017 1042704 doi`
12. `Harmel Chami Tormos Reynaud Danis 2018 sunglint Sentinel 2 coastal inland waters 213 138 153`
13. `Sentinel-2 marine atmospheric correction 6SV FLAASH QUAC DOS validation shallow water 2024`
14. `"Sensor-generic adjacency-effect correction" pdf`
15. `"A generalized physics-based correction for adjacency effects" pdf`
16. `"Evaluation of Sentinel-2/MSI" "1099" pdf`
17. `"Atmospheric correction in presence of sun glint" pdf`
18. `"Sensor-generic adjacency-effect correction" Wu 2025 full text`
19. `"Sunglint correction" "Harmel" 2018 pdf`
20. `"Sensitivity Assessment" "3492322" pdf`
21. `"Sentinel-2" "Banc" "atmospheric correction"`
22. `"10.1109/JSTARS.2024.3492322" filetype:pdf`
23. `"Sensor-generic adjacency-effect correction" "pdf" -site:researchgate.net -site:sciencedirect.com -site:scribd.com`
24. `"Atmospheric correction in presence of sun glint" site:hygeos.com`
25. `"Atmospheric correction in presence of sun glint" -site:researchgate.net -site:scispace.com -site:isprambiente.gov.it pdf`
26. `"Sensor-generic adjacency-effect correction" site:ntrs.nasa.gov`
27. `"Sensitivity Assessment of Atmospheric Corrections" Lathif publisher`
28. `"Retrieval of water-leaving radiance and aerosol optical thickness" pdf 1994`

Initial search terms contained unverified dates, page ranges, author combinations, or numeric identifiers. These were search hypotheses, not accepted metadata. Verification corrected the DSF DOI to 10.1016/j.rse.2019.03.010; the Harmel paper to 2018, volume 204, pp. 308–321; the French coastal paper to Bui et al. (2022); the Adriatic paper to Vrdoljak and Kilić Pamuković (2022); and the T-Mart paper to Wu et al. (2024). Corrections preceded bibliography export.

## Structured queries and citation chaining

- Crossref: `/works/{DOI}` for every DOI-bearing selected source; `/works?query.title=Sensitivity%20Assessment%20of%20Atmospheric%20Corrections%20for%20Clear%20and%20Moderately%20Turbid%20Optical%20Waters&rows=1` for DOI discovery.
- OpenAlex: `/works/https://doi.org/{DOI}` for legitimate full-text locations. Location metadata was checked against actual responses; an OA label alone did not establish a valid PDF.
- Chaining: references and method discussions in Warren 2019 and Pahlevan 2021 led to original processor descriptions and earlier assumptions; newer adjacency papers and official C2RCC references led to the 2024–2026 additions. No complete forward-citation census was performed.
- Direct institutional/publisher PDF routes and outcomes are stored per source in `../outputs/source_records.json`.

## Selection and exclusion

Include direct Sentinel-2 aquatic comparisons, relevant original algorithm descriptions, explicit mechanisms (glint/adjacency), and coastal bathymetry evidence. Prefer field-radiometry validation, while retaining clearly marked indirect inland-water evidence and foundational SeaWiFS/MERIS descriptions. Conference proceedings support processor provenance and are not treated as equivalent validation to multi-site intercomparisons.

Do not infer marine accuracy from land-only validation, a downstream fitted model alone, an article title, a promotional claim, or a preprint abstract. Hyperspectral-only ACIX-III/PRISMA work and inland-only generic-correction studies surfaced in search but were outside the core MSI marine comparison. The 2026 C2RCC paper supports method assumptions and sensor-transfer limits, not a new MSI comparison.

The library contains 17 selected references; it is not an exhaustive screened database. Relevant passages were inspected for 16 sources (15 PDFs and Wu's publisher HTML). Steinmetz 2011 remains abstract-only. No formal screened/excluded count can be reconstructed from these targeted web searches, and none is reported.

## Access, metadata, and limitations

Public access conditions were respected; no authentication or paywall was bypassed. Early Crossref requests received HTTP 429 responses; bounded later requests succeeded and failures were not interpreted as nonexistent publications. HTML/challenge responses were rejected as PDFs. Steinmetz's publisher PDF route did not yield a valid PDF. Wu's publisher PDF attempt was rejected, but the full primary article was readable through the web tool. Institutional sources provided other full texts.

Download records, resolved URLs, SHA-256 hashes, publication identity, inspection locations, and limitations are retained. PDFs are local research-library copies excluded from Git and the handoff archive. Shared root bibliography integration is deferred to the protected synchronization workflow; this task exports a self-contained library under its analysis directory.
