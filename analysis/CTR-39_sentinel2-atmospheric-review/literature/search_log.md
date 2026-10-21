# Targeted search record — exposed intertidal sediment revision

Search date: 20 October 2026. Scope changed by the authenticated user comment on CTR-39: exposed intertidal sediment at low tide; no water-column component. The previous search record is preserved in provenance/previous-water-review/literature/search_log.md.

## Research and selection

Target: atmospheric correction of sediment surface reflectance, with moisture, texture, microphytobenthos and exposure controls. Search scope is international, with particular attention to West African intertidal applications. This targeted review has no exhaustive screening protocol and is not systematic.

Queries used through web search:

- Sentinel-2 exposed intertidal sediment atmospheric correction Sen2Cor ACOLITE microphytobenthos
- Sentinel-2 tidal flats sediment atmospheric correction Sen2Cor LaSRC comparison
- Sentinel-2 intertidal sediment moisture atmospheric correction microphytobenthos radiometric
- Zoffoli 2020 Sentinel-2 intertidal vegetation atmospheric correction
- Sentinel-2 intertidal sediment moisture grain size atmospheric correction exposed mudflat study
- Atmospheric Correction Inter-comparison 113412 pdf
- Monitoring intertidal ecosystems 2025 atmospheric correction
- 3260 2022 intertidal sediment Sentinel
- MAJA multi temporal atmospheric correction Hagolle 2015 7 2668
- exact DOI/title searches for Thuy2022 and Zoffoli2020
- Sen2Cor BOA_ADD_OFFSET Copernicus processing baseline

Selection: read methods/results passages for direct exposed-surface validation and applications; add land benchmarks and official product definitions. Exclude water-only performance rankings from inference about exposed sediment. Existing water sources remain indexed for traceability. Relevant citation chaining: Zoffoli -> Main-Knorn; Granadeiro -> DSF; Henriques -> Granadeiro; ACIX-II -> Colin's complementary MAJA validation. A 2026 bathymetry paper was screened out because its submerged-water endpoint conflicts with revised scope. ACIX-III EnMAP/PRISMA was not adopted as direct MSI evidence. General Mediterranean-land and forest comparisons were screened as less direct than the selected sources, without claiming their irrelevance to other questions.

## Verification and access

Nine additional research papers were verified using Crossref metadata (direct works API or DOI CSL negotiation), and title/author/year/DOI/venue compared with PDF first pages. Crossref returned HTTP 429 for four concurrent metadata requests; DOI content negotiation resolved these. Full-text methods and relevant discussion/results were read; PDF extraction is retained locally, outside Git. Every added paper has a valid locally stored full-text PDF and checksum.

Public sources: Frontiers; PLOS; MDPI public asset server; NASA NTRS for Doxani and Colin; Universidad de Cádiz repository for Zoffoli; Universidad de Granada repository for Zarzuelo; Kyoto University for Thuy. No access control bypass was used. IEEE's public OA PDF endpoint returned 418 and obsolete Kyoto paths returned HTML. OpenAlex identified the repository bitstream. The public DSpace content endpoint returned a valid PDF, matching title/DOI and CC BY statement. Failed HTML responses were not saved as PDFs.

Official SentiWiki S2 Products was read for surface-reflectance encoding, nodata and band-resolution information. It is undated HTML, recorded as technical documentation with an access date, not a peer-reviewed article or a publication dated 2026. No standalone PDF of that webpage was identified; the separately linked product specification is not substituted for it.

## Critical observations

- Zoffoli atmospheric validation is restricted to two Bourgneuf scenes, despite broader seagrass algorithm validation.
- Daggers and Jacobs combine Sen2Cor with relative or angular corrections; use alone does not establish Sen2Cor accuracy.
- Thuy's claim of ELM superiority is not directly tested in that study; the review does not inherit it.
- Henriques §2.5.1 names ATCOR-2/3 while describing downloaded L2A; processor identity is not treated as verified. The paper is used for habitat/surface-state evidence.
- Granadeiro and Zarzuelo validate application endpoints, not a common correction ranking. Zarzuelo describes intermediate-tide selection in §3.1 / PDF p. 7 but limits habitat zonation to low tide in the Discussion / PDF p. 12. The methods distinguish extent detection from habitat classification, but the relationship between the selection statements remains unclear; no stage-specific tidal rule is inferred. Low-tide exposed-sediment selection is retained.
- ACIX-II Land excludes some methods from a surface-reflectance analysis and contains model/reference differences. Colin supplies complementary MAJA evidence but not a tidal-flat comparison.

Remaining gap: no local Banc d’Arguin exposed-sediment processor validation was established in this targeted search. This is not proof that no such study exists. Source-specific passages and limitations are in the evidence matrix.

## Focused correction after independent review

On 20 October 2026, the author re-inspected Zarzuelo PDF pp. 7 and 12 and Doxani PDF p. 9 in the existing hash-verified primary full texts. CTR-45 M1 is addressed by recording both tidal-selection statements and their unresolved relationship; E1 corrects the ACIX-II passage to §3.1.3. The authoritative notes, report and generated evidence/index are updated. No new search, reference, local performance result or processor ranking is introduced. The corrected submission awaits a focused independent recheck.
