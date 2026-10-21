# Remote-sensing QA summary

**Take-home message:** Computational checks pass for the paired reflectance delivery. They do not establish atmospheric-correction accuracy or constitute independent scientific approval.

**Meaningful results:** 22 matched sensor/datatake/orbit/tile acquisitions; B2/B3/B4/B8 dimensionless ΔR = ACOLITE − Sen2Cor; exact native 10 m comparison grid in EPSG:32628. 113 rasters pass grid/type/NoData checks, 12 source-pixel comparisons pass (maximum absolute discrepancy 7.12e-10), and 96 temporal checks agree with base R. Full-grid validity masks match n≥1 for median and n≥2 for sample SD. Input manifests cover 142 physical files and 22.2 GB.

**Issues and limitations:** Every ACOLITE band contains 118,596 encoded default-fill cells despite NoData=NaN; the exact sentinel is explicitly rejected and separately audited in all 88 source bands. March 2026 lacks ACOLITE flags. Masks and ecological interpretations have no independent field validation; temporal and spatial dependence and changing support remain relevant.

**Implications and next steps:** Use the coverage sensitivities and downstream table contract. Submit this bounded geospatial delivery through the existing CTR-54 review chain. Independent review and PI approval remain pending.

Input metadata, wavelength/units/offset verification, all source/output grid checks, masks, exclusions, resampling, numerical checks and versions are retained in tables/ and provenance/. See METHODS.md for detail. Raw inputs are read only; their sizes/mtimes still match the hash pass. No manuscript changes, integration, merge or publication are authorized by this delivery.
